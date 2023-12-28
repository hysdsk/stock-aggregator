import os
import re
from multiprocessing import Pool, cpu_count
from .output import Output
from .processor import Processor
from .printer import CsvPrinter


class Workflow(object):
    def __init__(self, destination: str, allowed_symbols: list[str] = None) -> None:
        self.processor = Processor()
        self.printer = CsvPrinter(destination)
        self.allowed_symbols = allowed_symbols

    def _findFiles(self, dirName: str) -> list[str]:
        pattern_json = re.compile(r"^[0-9]{4}\.json$")
        files = os.listdir(dirName)
        if "incomplete" in files:
            return []
        files = [f for f in files if pattern_json.match(f)]
        if self.allowed_symbols:
            files = [f for f in files if f.replace(".json", "") in self.allowed_symbols]
        else:
            files = [f for f in files if f.replace(".json", "") not in ["101", "151", "154"]]
        return [f"{dirName}/{f}" for f in files]

    def _readFile(self, filename: str) -> list[str]:
        with open(filename, mode="r", encoding="utf-8") as f:
            return f.readlines()

    def run(self, dirName: str) -> None:
        files = self._findFiles(dirName)
        outputs: list[Output] = []
        with Pool(processes=cpu_count()) as pool:
            results = pool.starmap_async(self.processor.run, [(self._readFile(file),) for file in files])
            outputs.extend(results.get())
        self.printer.out(outputs)
