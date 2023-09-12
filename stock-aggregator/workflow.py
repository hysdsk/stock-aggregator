import os
import re
import pandas as pd
from configparser import ConfigParser
from argparse import Namespace
from .processor import Processor
from .printer import Printer


class Workflow(object):
    def __init__(self, targetdate: str, args: Namespace) -> None:
        configparser = ConfigParser()
        configparser.read("config.ini")
        self.config = configparser["DEFAULT"]
        self.targetdate = targetdate
        self.args = args
        df = pd.read_csv(self.config["target_filename"], dtype={"code": str}, skipinitialspace=True).rename(columns=lambda x: x.strip())
        self.thresholds = { target["code"]: target["th_value"] * 10000 for target in df.to_dict("records") }

    def _find_directory(self) -> list[str]:
        pattern_json = re.compile(r"^[0-9]{4}\.json$")
        files = os.listdir(f"{self.config['tickdata_directory']}/{self.targetdate}")
        if "incomplete" in files:
            return []
        symbols = [f.replace(".json", "") for f in files if pattern_json.match(f)]
        symbols = [s for s in symbols if s not in ["101", "151", "154"]]
        symbols = [s for s in symbols if s in self.thresholds]
        return symbols

    def _read_file(self, symbol: str) -> list[str]:
        filename = f"{self.config['tickdata_directory']}/{self.targetdate}/{symbol}.json"
        with open(filename, mode="r", encoding="utf-8") as f:
            return f.readlines()

    def run(self, printer: Printer):
        symbols = self._find_directory()
        for symbol in symbols:
            lines = self._read_file(symbol)
            proccesor: Processor = Processor(self.args.buy, self.args.sell, self.args.offset_minute, self.args.close, self.thresholds)
            output = proccesor.run(lines)
            printer.out(output)
