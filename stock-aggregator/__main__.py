import os
import json
import re
from configparser import ConfigParser
from argparse import ArgumentParser
from datetime import datetime
import pandas as pd
from kabustation.message import Message
from .output import Output
from .printer import Printer
from .processor import ContractProcessor


# Global
configparser = ConfigParser()
configparser.read("config.ini")
config = configparser["DEFAULT"]

parser = ArgumentParser()
parser.add_argument("--day", type=str, default=None, help="")
parser.add_argument("--close", type=int, default=15, choices=[10, 11, 12, 13, 14, 15], help="")
parser.add_argument("--output", type=str, default="console", choices=["console", "csv"], help="")
parser.add_argument("--item", type=str, default="short", choices=["short", "full"], help="")
parser.add_argument("--buy", type=int, default=1, help="")
parser.add_argument("--sell", type=int, default=1, help="")
args = parser.parse_args()

am8 = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
close_time = datetime.now().replace(hour=args.close, minute=0, second=0, microsecond=0)

df = pd.read_csv(config["target_filename"], dtype={"code": str}, skipinitialspace=True).rename(columns=lambda x: x.strip())
thresholds = { target["code"]: target["th_value"] * 10000 for target in df.to_dict("records") }

printer = Printer(item=args.item, output=config["output_csvname"]) if args.output == "csv" else Printer(item=args.item)


# each data
def check_data(lines: list):
    cp = ContractProcessor(thresholds, args.buy, args.sell)
    output = Output()
    messages: list[Message] = []
    for line in lines:
        crnt = Message(json.loads(line))
        if crnt.receivedTime.time() < am8.time():
            continue
        if crnt.receivedTime.time() >= close_time.time():
            break

        messages.append(Message(json.loads(line)))
        if cp.run(messages, output) == 1:
            break

    if output.buy_count >= args.buy:
        output.out_price = messages[-1].currentPrice
        output.out_time = messages[-1].currentPriceTime
        if args.output == "csv":
            printer.out_csv(messages[-1], output)
        else:
            printer.out_console(messages[-1], output)

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
        print(f"{targetdate} is incomplete files.")
        return

    for file in [f for f in files if pattern_json.match(f)]:
        code = file.replace(".json", "")
        if code in ["101", "151", "154"] or code not in thresholds:
            print(f"Not found \"{code}\" in symbols csv.")
            continue
        open_file(targetdate, file)

if __name__ == "__main__":
    print("Now aggregating ...")
    try:
        if args.day is None:
            for targetdate in os.listdir(config["tickdata_directory"]):
                main(targetdate)
        elif re.compile(r"^[0-9]{6}$").match(args.day):
            for targetdate in os.listdir(config["tickdata_directory"]):
                if targetdate.startswith(args.day): main(targetdate)
        elif re.compile(r"^[0-9]{8}$").match(args.day):
            main(args.day)
        else:
            print(f"Invalid day: {args.day}")
    finally:
        printer.close_writer()
