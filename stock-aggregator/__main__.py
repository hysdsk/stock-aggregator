import os
import re
from tqdm import tqdm
from configparser import ConfigParser
from argparse import ArgumentParser
from .workflow import Workflow
from .printer import Printer, ConsolePrinter, CsvPrinter


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


if __name__ == "__main__":
    printer: Printer = CsvPrinter(args.buy, args.sell) if args.output == "csv" else ConsolePrinter()
    try:
        targetdatelist = os.listdir(config["tickdata_directory"])
        if args.day and re.compile(r"^[0-9]{6}$").match(args.day):
            targetdatelist = [t for t in targetdatelist if t.startswith(args.day)]
        elif args.day and re.compile(r"^[0-9]{8}$").match(args.day):
            targetdatelist = [t for t in targetdatelist if t == args.day]
        if args.output == "csv":
            print(f"The output destination is {printer.csvname}")
            desc=f"Aggregate data for {len(targetdatelist)} days"
            bar_format="{l_bar}\033[32m{bar}\033[0m{r_bar}"
            for targetdate in tqdm(targetdatelist, desc=desc, bar_format=bar_format):
                Workflow(targetdate, args).run(printer)
        else:
            for targetdate in targetdatelist:
                Workflow(targetdate, args).run(printer)
    except KeyboardInterrupt:
        print("You typed \"CTRL + C\", which is the keyboard interrupt exception.")
    finally:
        printer.close()
        print("Aggregation has finished.")
