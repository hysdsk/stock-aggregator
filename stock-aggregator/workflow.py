import os
import re
from multiprocessing import Pool, cpu_count
from .processor import Processor
from .output import Output


class Workflow(object):
    def __init__(self, thresholds: dict[str, int] = None) -> None:
        self.thresholds = thresholds

    def _findFiles(self, dirName: str) -> list[str]:
        pattern_json = re.compile(r"^[0-9]{4}\.json$")
        files = os.listdir(dirName)
        if "incomplete" in files:
            return []
        files = [f for f in files if pattern_json.match(f)]
        files = [f for f in files if f.replace(".json", "") not in ["101", "151", "154"]]
        files = [f for f in files if self.thresholds is None or f.replace(".json", "") in self.thresholds]
        return [f"{dirName}/{f}" for f in files]

    def _readFile(self, filename: str) -> list[str]:
        with open(filename, mode="r", encoding="utf-8") as f:
            return f.readlines()

    def run(self, dirName: str, offset_minute: int) -> list[Output]:
        outputs: list[Output] = []
        files = self._findFiles(dirName)
        processor: Processor = Processor(offset_minute, self.thresholds)
        with Pool(processes=cpu_count()) as pool:
            results = pool.starmap_async(processor.run, [(self._readFile(file),) for file in files])
            outputs.extend(results.get())
        return outputs
