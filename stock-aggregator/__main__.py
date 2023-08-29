import os
import json
import re
from configparser import ConfigParser
from argparse import ArgumentParser
from datetime import datetime
import pandas as pd
from kabustation.message import Message
from .printer import Printer


# Global
configparser = ConfigParser()
configparser.read("config.ini")
config = configparser["DEFAULT"]

parser = ArgumentParser()
parser.add_argument("--day", type=str, default=None, help="")
parser.add_argument("--close", type=int, default=15, choices=[10, 11, 12, 13, 14, 15], help="")
parser.add_argument("--mode", type=str, default="console", choices=["console", "csv"], help="")
args = parser.parse_args()

am8 = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
close_time = datetime.now().replace(hour=args.close, minute=0, second=0, microsecond=0)

df = pd.read_csv(config["target_filename"], dtype={"code": str}, skipinitialspace=True).rename(columns=lambda x: x.strip())
thresholds = { target["code"]: target["th_value"] * 10000 for target in df.to_dict("records") }

printer = Printer(config["output_csvname"]) if args.mode == "csv" else Printer()

# Sell or Buy
def sellorbuy(crnt: Message, prev: Message):
    prevprice = crnt.previousClose if prev.is_preparing() else prev.currentPrice
    if prevprice:
        if crnt.currentPrice < prevprice:
            return -1
        if crnt.currentPrice > prevprice:
            return 1
        if prev.askPrice and prevprice <= prev.askPrice:
            return -1
        if prev.bidPrice and prevprice >= prev.bidPrice:
            return 1
    return 0

# each data
def check_data(lines: list):
    output = {
        "buy_price": None,
        "buy_time": None,
        "buy_count": 0,
        "buy_tradingvalue": None,
        "out_price": None,
        "out_time": None,
        "high_price": None,
        "low_price": None,
    }
    messages: list[Message] = []
    for line in lines:
        crnt = Message(json.loads(line))
        if crnt.receivedTime.time() < am8.time():
            continue
        if crnt.receivedTime.time() >= close_time.time():
            break

        messages.append(Message(json.loads(line)))
        if len(messages) < 2:
            continue
        prev = messages[-2]
        if prev.currentPrice is None:
            continue

        if output["buy_price"] is not None:
            if output["high_price"] < crnt.currentPrice:
                output["high_price"] = crnt.currentPrice
            if output["low_price"] > crnt.currentPrice:
                output["low_price"] = crnt.currentPrice

        value = crnt.tradingValue - prev.tradingValue
        if value > thresholds[crnt.symbol]:
            sob = sellorbuy(crnt, prev)
            if sob > 0:
                if output["buy_price"] is None:
                    output["buy_price"] = crnt.currentPrice
                    output["buy_time"] = crnt.currentPriceTime
                    output["buy_tradingvalue"] = crnt.tradingValue
                    output["high_price"] = crnt.currentPrice
                    output["low_price"] = crnt.currentPrice
                output["buy_count"] += 1
            elif sob < 0:
                if output["buy_count"] > 0:
                   break

    if output["buy_count"] > 0:
        output["out_price"] = messages[-1].currentPrice
        output["out_time"] = messages[-1].currentPriceTime
        if args.mode == "csv":
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
