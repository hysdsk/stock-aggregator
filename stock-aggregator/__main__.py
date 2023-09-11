import os
import json
import re
from tqdm import tqdm
from configparser import ConfigParser
from argparse import ArgumentParser
from datetime import datetime
import pandas as pd
from kabustation.message import Message
from .output import Output
from .printer import Printer
from .processor import Processor


# Global
configparser = ConfigParser()
configparser.read("config.ini")
config = configparser["DEFAULT"]

parser = ArgumentParser()
parser.add_argument("--day", type=str, default=None, help="")
parser.add_argument("--close", type=int, default=15, choices=range(10, 16), help="")
parser.add_argument("--output", type=str, default="console", choices=["console", "csv"], help="")
parser.add_argument("--buy", type=int, default=1, help="")
parser.add_argument("--sell", type=int, default=1, help="")
parser.add_argument("--offset-minute", type=int, default=5, choices=range(1, 31), help="")
args = parser.parse_args()

am8 = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
close_time = datetime.now().replace(hour=args.close, minute=0, second=0, microsecond=0)
if args.close == 15:
    close_time = datetime.now().replace(hour=14, minute=59, second=50, microsecond=0)

df = pd.read_csv(config["target_filename"], dtype={"code": str}, skipinitialspace=True).rename(columns=lambda x: x.strip())
thresholds = { target["code"]: target["th_value"] * 10000 for target in df.to_dict("records") }

outdir = config["output_directory"][:-1] if config["output_directory"][-1] == "/" else config["output_directory"]
csvname = f"{outdir}/aggregated.{int(datetime.now().timestamp())}.csv"
printer = Printer(distfile=csvname) if args.output == "csv" else Printer()


# each data
def check_data(lines: list):
    threshold = thresholds[Message(json.loads(lines[0])).symbol]
    openingTotalMarketValue = None
    for line in lines:
       msg = Message(json.loads(line))
       if msg.totalMarketValue:
           openingTotalMarketValue = msg.totalMarketValue
           break
    proccesor: Processor = Processor(threshold, args.buy, args.sell, args.offset_minute)
    output = Output()
    messages: list[Message] = []
    for line in lines:
        crnt = Message(json.loads(line))
        if crnt.receivedTime.time() < am8.time():
            continue
        if crnt.receivedTime.time() >= close_time.time():
            break
        messages.append(Message(json.loads(line)))
        proccesor.run(messages, output)
    if args.output == "csv":
        printer.out_csv(messages[-1], output, threshold, openingTotalMarketValue)
    else:
        printer.out_console(messages[-1], output, threshold, openingTotalMarketValue)

# each symbol process
def open_file(targetdate: int, file: str):
    filename = f"{config['tickdata_directory']}/{targetdate}/{file}"
    with open(filename, mode="r", encoding="utf-8") as f:
        check_data(f.readlines())

# main process
def main(targetdate: str):
    pattern_json = re.compile(r"^[0-9]{4}\.json$")
    files = os.listdir(f"{config['tickdata_directory']}/{targetdate}")
    if "incomplete" in files:
        return

    for file in [f for f in files if pattern_json.match(f)]:
        code = file.replace(".json", "")
        if code in ["101", "151", "154"] or code not in thresholds:
            continue
        open_file(targetdate, file)

if __name__ == "__main__":
    try:
        targetdatelist = os.listdir(config["tickdata_directory"])
        if args.day and re.compile(r"^[0-9]{6}$").match(args.day):
            targetdatelist = [t for t in targetdatelist if t.startswith(args.day)]
        elif args.day and re.compile(r"^[0-9]{8}$").match(args.day):
            targetdatelist = [t for t in targetdatelist if t == args.day]
        if args.output == "csv":
            print(f"The output destination is {csvname}")
            desc=f"Aggregate data for {len(targetdatelist)} days"
            bar_format="{l_bar}\033[32m{bar}\033[0m{r_bar}"
            for targetdate in tqdm(targetdatelist, desc=desc, bar_format=bar_format):
                main(targetdate)
        else:
            for targetdate in targetdatelist:
                main(targetdate)
    except KeyboardInterrupt:
        print("You typed \"CTRL + C\", which is the keyboard interrupt exception.")
    finally:
        printer.close_writer()
        print("Aggregation has finished.")
