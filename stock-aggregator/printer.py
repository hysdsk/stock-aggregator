import copy
import pandas as pd
from abc import ABC, abstractmethod
from datetime import datetime
from configparser import ConfigParser
from console import Formater
from .output import Output


class Printer(ABC):
    def __init__(self):
        configparser = ConfigParser()
        configparser.read("config.ini")
        self.config = configparser["DEFAULT"]

    def get_jp_week(self, thatday: datetime):
        num = thatday.weekday()
        if num == 0: return "月"
        if num == 1: return "火"
        if num == 2: return "水"
        if num == 3: return "木"
        if num == 4: return "金"
        if num == 5: return "土"
        return "日"

    @abstractmethod
    def out(self, outputs: list[Output]):
        pass


class ConsolePrinter(Printer):
    def __init__(self):
        super().__init__()
        self.items = [
            "日付",
            "曜日",
            "銘柄コード",
            "銘柄名",
            "閾値",
            "前日終値",
            "前日時価総額",
            "寄付時間",
            "寄付価格",
            "寄時売買代金",
            "当日高値時間",
            "当日高値",
            "当日安値時間",
            "当日安値",
            "当日終値",
            "当日売買代金",
            "買約定回数",
            "売約定回数",
        ]
        for i, item in enumerate(self.items):
            print(f"{str(i+1).rjust(2)}. {item}")

    def out(self, outputs: list[Output]):
        for output in outputs:
            if output.last_message.is_preparing(): return
            template = " ".join(["{}"]*len(self.items))
            print(template.format(
                output.last_message.receivedTime.strftime("%Y/%m/%d"),
                self.get_jp_week(output.last_message.receivedTime),
                output.last_message.symbol,
                Formater(output.last_message.symbolName).sname().value,
                Formater(output.threshold).volume().value,
                Formater(output.last_message.previousClose).price().gray().value,
                Formater(output.opening_totalmarketvalue).volume().value,
                Formater(output.last_message.openingPriceTime).time().value,
                Formater(output.last_message.openingPrice).price().green().value,
                Formater(output.opening_tradingvalue).volume().value,
                Formater(output.last_message.highPriceTime).time().value,
                Formater(output.last_message.highPrice).price().value,
                Formater(output.last_message.lowPriceTime).time().value,
                Formater(output.last_message.lowPrice).price().value,
                Formater(output.last_message.currentPrice).price().value,
                Formater(output.last_message.tradingValue).volume().value,
                str(len(output.buyContracts)).rjust(2),
                str(len(output.sellContracts)).rjust(2),
            ))


class CsvPrinter(Printer):
    def __init__(self, csvname):
        super().__init__()
        self.csvname = csvname
        self.base = {
            "日付": [],
            "曜日": [],
            "銘柄コード": [],
            "銘柄名": [],
            "閾値": [],
            "前日終値": [],
            "前日時価総額": [],
            "寄付時間": [],
            "寄付価格": [],
            "寄時売買代金": [],
            "当日高値時間": [],
            "当日高値": [],
            "当日安値時間": [],
            "当日安値": [],
            "当日終値": [],
            "当日売買代金": [],
            "買約定回数": [],
            "売約定回数": [],
        }
        for i in range(1, 4):
            self.base[f"{i}:前場寄前注文時間"] = []
            self.base[f"{i}:前場寄前注文代金"] = []
        for i in range(1, 4):
            self.base[f"{i}:後場寄前注文時間"] = []
            self.base[f"{i}:後場寄前注文代金"] = []
        for i in range(1, 10):
            self.base[f"{i}:買約定時間"] = []
            self.base[f"{i}:買約定価格"] = []
            self.base[f"{i}:買約定直前価格"] = []
            self.base[f"{i}:買時VWAP"] = []
            self.base[f"{i}:買時売買代金"] = []
            self.base[f"{i}:買時売買代金一分"] = []
            self.base[f"{i}:買時板更新数一分"] = []
            self.base[f"{i}:買後高値時間"] = []
            self.base[f"{i}:買後高値"] = []
            self.base[f"{i}:買後安値時間"] = []
            self.base[f"{i}:買後安値"] = []
        for i in range(1, 10):
            self.base[f"{i}:売約定時間"] = []
            self.base[f"{i}:売約定価格"] = []
            self.base[f"{i}:売約定直前価格"] = []
            self.base[f"{i}:売時VWAP"] = []
            self.base[f"{i}:売時売買代金"] = []
            self.base[f"{i}:売時売買代金一分"] = []
            self.base[f"{i}:売時板更新数一分"] = []
        pd.DataFrame(self.base).to_csv(csvname, index=False)

    def out(self, outputs: list[Output]):
        for output in outputs:
            data = copy.deepcopy(self.base)
            if output.last_message.is_preparing(): return
            data["日付"].append(output.last_message.receivedTime.strftime("%Y/%m/%d"))
            data["曜日"].append(self.get_jp_week(output.last_message.receivedTime))
            data["銘柄コード"].append(output.last_message.symbol)
            data["銘柄名"].append(output.last_message.symbolName)
            data["閾値"].append(output.threshold)
            data["前日終値"].append(output.last_message.previousClose)
            data["前日時価総額"].append(output.opening_totalmarketvalue)
            data["寄付時間"].append(Formater(output.last_message.openingPriceTime).time().value)
            data["寄付価格"].append(output.last_message.openingPrice)
            data["寄時売買代金"].append(output.opening_tradingvalue)
            data["当日高値時間"].append(Formater(output.last_message.highPriceTime).time().value)
            data["当日高値"].append(output.last_message.highPrice)
            data["当日安値時間"].append(Formater(output.last_message.lowPriceTime).time().value)
            data["当日安値"].append(output.last_message.lowPrice)
            data["当日終値"].append(output.last_message.currentPrice)
            data["当日売買代金"].append(output.last_message.tradingValue)
            data["買約定回数"].append(len(output.buyContracts))
            data["売約定回数"].append(len(output.sellContracts))
            for i in range(1, 4):
                flg = len(output.firstOrders) >= i
                data[f"{i}:前場寄前注文時間"].append(output.firstOrders[i-1].thatTime.time() if flg else None)
                data[f"{i}:前場寄前注文代金"].append(output.firstOrders[i-1].orderValue if flg else None)
            for i in range(1, 4):
                flg = len(output.laterOrders) >= i
                data[f"{i}:後場寄前注文時間"].append(output.laterOrders[i-1].thatTime.time() if flg else None)
                data[f"{i}:後場寄前注文代金"].append(output.laterOrders[i-1].orderValue if flg else None)
            for i in range(1, 10):
                flg = len(output.buyContracts) >= i
                data[f"{i}:買約定時間"].append(output.buyContracts[i-1].thatTime.time() if flg else None)
                data[f"{i}:買約定価格"].append(output.buyContracts[i-1].price if flg else None)
                data[f"{i}:買約定直前価格"].append(output.buyContracts[i-1].prevPrice if flg else None)
                data[f"{i}:買時VWAP"].append(output.buyContracts[i-1].vwap if flg else None)
                data[f"{i}:買時売買代金"].append(output.buyContracts[i-1].tradingValue if flg else None)
                data[f"{i}:買時売買代金一分"].append(output.buyContracts[i-1].tradingValueByMinute if flg else None)
                data[f"{i}:買時板更新数一分"].append(output.buyContracts[i-1].updateCountByMinute if flg else None)
                data[f"{i}:買後高値時間"].append(output.buyContracts[i-1].highPriceTime.replace(microsecond=0).time() if flg else None)
                data[f"{i}:買後高値"].append(output.buyContracts[i-1].highPrice if flg else None)
                data[f"{i}:買後安値時間"].append(output.buyContracts[i-1].lowPriceTime.replace(microsecond=0).time() if flg else None)
                data[f"{i}:買後安値"].append(output.buyContracts[i-1].lowPrice if flg else None)
            for i in range(1, 10):
                flg = len(output.sellContracts) >= i
                data[f"{i}:売約定時間"].append(output.sellContracts[i-1].thatTime.time() if flg else None)
                data[f"{i}:売約定価格"].append(output.sellContracts[i-1].price if flg else None)
                data[f"{i}:売約定直前価格"].append(output.sellContracts[i-1].prevPrice if flg else None)
                data[f"{i}:売時VWAP"].append(output.sellContracts[i-1].vwap if flg else None)
                data[f"{i}:売時売買代金"].append(output.sellContracts[i-1].tradingValue if flg else None)
                data[f"{i}:売時売買代金一分"].append(output.sellContracts[i-1].tradingValueByMinute if flg else None)
                data[f"{i}:売時板更新数一分"].append(output.sellContracts[i-1].updateCountByMinute if flg else None)
            pd.DataFrame(data).to_csv(self.csvname, index=False, header=False, mode="a")
