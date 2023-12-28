import os
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from configparser import ConfigParser
from argparse import ArgumentParser
from .workflow import Workflow


def getTargets(day: str, dirName: str):
    targets = {target: f"{dirName}/{target}" for target in os.listdir(dirName)}
    return {k: v for k, v in targets.items() if k.startswith(day)} if day else targets

if __name__ == "__main__":
    # プロパティ取得
    configparser = ConfigParser()
    configparser.read("config.ini")
    config = configparser["DEFAULT"]
    # コマンド引数取得
    parser = ArgumentParser()
    parser.add_argument("--day", type=str, default=None, help="")
    parser.add_argument("--symbols", type=str, default=None, nargs="+", help="")
    args = parser.parse_args()
    # 閾値読み込み
    df = pd.read_csv(config["target_filename"], dtype={"code": str}, skipinitialspace=True).rename(columns=lambda x: x.strip())
    # 集計元データ選定
    targets = getTargets(args.day, config["tickdata_directory"])
    try:
        destination = f"output/csv/aggregated.{int(datetime.now().timestamp())}.csv"
        print(f"The output destination is {destination}")
        desc=f"Aggregate data for {len(targets.items())} days"
        bar_format="{l_bar}\033[32m{bar}\033[0m{r_bar}"
        for day, dirName in tqdm(targets.items(), desc=desc, bar_format=bar_format):
            Workflow(destination, args.symbols).run(dirName)
    except KeyboardInterrupt:
        print("You typed \"CTRL + C\", which is the keyboard interrupt exception.")
    finally:
        print("Aggregation has finished.")
