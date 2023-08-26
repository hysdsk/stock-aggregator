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
parser.add_argument("--day", type=int, default=0, help="")
parser.add_argument("--close", type=int, default=15, choices=[10, 11, 12, 13, 14, 15], help="")
args = parser.parse_args()

am8 = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
close_time = datetime.now().replace(hour=args.close, minute=0, second=0, microsecond=0)

df = pd.read_csv(config["target_filename"], dtype={"code": str}, skipinitialspace=True).rename(columns=lambda x: x.strip())
thresholds = { target["code"]: target["th_value"] * 10000 for target in df.to_dict("records") }


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
        "out_price": None,
        "out_time": None,
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

        value = crnt.tradingValue - prev.tradingValue
        if value > thresholds[crnt.symbol]:
            sob = sellorbuy(crnt, prev)
            if sob > 0:
                if output["buy_price"] is None:
                    output["buy_price"] = crnt.currentPrice
                    output["buy_time"] = crnt.currentPriceTime
                output["buy_count"] += 1
            elif sob < 0:
                if output["buy_count"] > 0:
                   break

    if output["buy_count"] > 0:
        output["out_price"] = messages[-1].currentPrice
        output["out_time"] = messages[-1].currentPriceTime
        Printer().out_print(messages[-1], output)

# each symbol process
def open_file(targetdate: int, file: str):
    filename = f"{config['tickdata_directory']}/{targetdate}/{file}"
    with open(filename, mode="r", encoding="utf-8") as f:
        check_data(f.readlines())

# main process
def main(targetdate: int):
    pattern_json = re.compile(r"^[0-9]{4}\.json$")
    files = os.listdir(f"{config['tickdata_directory']}/{targetdate}")
    if "incomplete" in files:
        print(f"{targetdate} is incomplete files.")
        return

    for file in [f for f in files if pattern_json.match(f)]:
        code = int(file.replace(".json", ""))
        if code in [101, 151, 154]:
            continue
        if code in thresholds:
            print(f"Not found symbol({code}) in symbols.csv .")
            continue
        open_file(targetdate, file)

if __name__ == "__main__":
    print("1. 日付")
    print("2. 銘柄コード")
    print("3. 銘柄名")
    print("4. 初回買大約定時間")
    print("5. 初回買大約定価格")
    print("6. 買大約定数")
    print("7. 初回売大約定時間（終了時含む）")
    print("8. 初回売大約定価格（終了時含む）")
    print("9. 価格騰落率")
    if args.day > 0:
        main(args.day)
    else:
        for targetdate in os.listdir(config["tickdata_directory"]):
            main(targetdate)
