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
        self.items = {
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
            "寄時成行買注文数": [],
            "寄時成行売注文数": [],
            "寄時指値買注文数": [],
            "寄時指値売注文数": [],
            "当日高値時間": [],
            "当日高値": [],
            "当日安値時間": [],
            "当日安値": [],
            "当日終値": [],
            "当日売買代金": [],
            "買大約定回数": [],
            "買大約定平均代金": [],
            "売大約定回数": [],
            "売大約定平均代金": [],
            "総買約定回数": [],
            "総買約定代金": [],
            "総売約定回数": [],
            "総売約定代金": [],
        }

    def out(self, outputs: list[Output]):
        data = copy.deepcopy(self.items)
        for output in outputs:
            if output.last_message.is_preparing(): return
            data["日付"].append(output.last_message.receivedTime.strftime("%Y/%m/%d"))
            data["曜日"].append(self.get_jp_week(output.last_message.receivedTime))
            data["銘柄コード"].append(output.last_message.symbol)
            data["銘柄名"].append(Formater(output.last_message.symbolName).sname().value)
            data["閾値"].append(Formater(output.threshold).volume().value)
            data["前日終値"].append(Formater(output.last_message.previousClose).price().gray().value)
            data["前日時価総額"].append(Formater(output.opening_totalmarketvalue).volume().value)
            data["寄付時間"].append(Formater(output.last_message.openingPriceTime).time().value)
            data["寄付価格"].append(Formater(output.last_message.openingPrice).price().green().value)
            data["寄時売買代金"].append(Formater(output.opening_tradingvalue).volume().value)
            data["寄時成行買注文数"].append(Formater(output.openingMarketOrderBuyQty).volume().value)
            data["寄時成行売注文数"].append(Formater(output.openingMarketOrderSellQty).volume().value)
            data["寄時指値買注文数"].append(Formater(output.openingLimitOrderBuyQty).volume().value)
            data["寄時指値売注文数"].append(Formater(output.openingLimitOrderSellQty).volume().value)
            data["当日高値時間"].append(Formater(output.last_message.highPriceTime).time().value)
            data["当日高値"].append(Formater(output.last_message.highPrice).price().value)
            data["当日安値時間"].append(Formater(output.last_message.lowPriceTime).time().value)
            data["当日安値"].append(Formater(output.last_message.lowPrice).price().value)
            data["当日終値"].append(Formater(output.last_message.currentPrice).price().value)
            data["当日売買代金"].append(Formater(output.last_message.tradingValue).volume().value)
            data["買大約定回数"].append(len(output.buyContracts))
            data["買大約定平均代金"].append(Formater(round(sum([b.tradingValue for b in output.buyContracts])/len(output.buyContracts)) if len(output.buyContracts) > 0 else 0).volume().value)
            data["売大約定回数"].append(len(output.sellContracts))
            data["売大約定平均代金"].append(Formater(round(sum([s.tradingValue for s in output.sellContracts])/len(output.sellContracts)) if len(output.sellContracts) > 0 else 0).volume().value)
            data["総買約定回数"].append(output.totalBuyCount)
            data["総買約定代金"].append(Formater(output.totalBuyValue).volume().value)
            data["総売約定回数"].append(output.totalSellCount)
            data["総売約定代金"].append(Formater(output.totalSellValue).volume().value)
        print(pd.DataFrame(data))


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
            "寄時成行買注文数": [],
            "寄時成行売注文数": [],
            "寄時指値買注文数": [],
            "寄時指値売注文数": [],
            "当日高値時間": [],
            "当日高値": [],
            "当日安値時間": [],
            "当日安値": [],
            "当日終値": [],
            "当日売買代金": [],
            "買大約定回数": [],
            "買大約定平均代金": [],
            "売大約定回数": [],
            "売大約定平均代金": [],
            "総買約定回数": [],
            "総買約定代金": [],
            "総売約定回数": [],
            "総売約定代金": [],
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
            self.base[f"{i}:買約定高値"] = []
            self.base[f"{i}:買約定安値"] = []
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
            self.base[f"{i}:売約定高値"] = []
            self.base[f"{i}:売約定安値"] = []
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
            data["寄時成行買注文数"].append(output.openingMarketOrderBuyQty)
            data["寄時成行売注文数"].append(output.openingMarketOrderSellQty)
            data["寄時指値買注文数"].append(output.openingLimitOrderBuyQty)
            data["寄時指値売注文数"].append(output.openingLimitOrderSellQty)
            data["当日高値時間"].append(Formater(output.last_message.highPriceTime).time().value)
            data["当日高値"].append(output.last_message.highPrice)
            data["当日安値時間"].append(Formater(output.last_message.lowPriceTime).time().value)
            data["当日安値"].append(output.last_message.lowPrice)
            data["当日終値"].append(output.last_message.currentPrice)
            data["当日売買代金"].append(output.last_message.tradingValue)
            data["買大約定回数"].append(len(output.buyContracts))
            data["買大約定平均代金"].append(round(sum([b.tradingValue for b in output.buyContracts])/len(output.buyContracts)) if len(output.buyContracts) > 0 else 0)
            data["売大約定回数"].append(len(output.sellContracts))
            data["売大約定平均代金"].append(round(sum([s.tradingValue for s in output.sellContracts])/len(output.sellContracts)) if len(output.sellContracts) > 0 else 0)
            data["総買約定回数"].append(output.totalBuyCount)
            data["総買約定代金"].append(output.totalBuyValue)
            data["総売約定回数"].append(output.totalSellCount)
            data["総売約定代金"].append(output.totalSellValue)
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
                data[f"{i}:買約定高値"].append(output.buyContracts[i-1].highPrice if flg else None)
                data[f"{i}:買約定安値"].append(output.buyContracts[i-1].lowPrice if flg else None)
                data[f"{i}:買時VWAP"].append(output.buyContracts[i-1].vwap if flg else None)
                data[f"{i}:買時売買代金"].append(output.buyContracts[i-1].tradingValue if flg else None)
                data[f"{i}:買時売買代金一分"].append(output.buyContracts[i-1].tradingValueByMinute if flg else None)
                data[f"{i}:買時板更新数一分"].append(output.buyContracts[i-1].updateCountByMinute if flg else None)
                data[f"{i}:買後高値時間"].append(output.buyContracts[i-1].highPriceAfterTime.replace(microsecond=0).time() if flg else None)
                data[f"{i}:買後高値"].append(output.buyContracts[i-1].highPriceAfter if flg else None)
                data[f"{i}:買後安値時間"].append(output.buyContracts[i-1].lowPriceAfterTime.replace(microsecond=0).time() if flg else None)
                data[f"{i}:買後安値"].append(output.buyContracts[i-1].lowPriceAfter if flg else None)
            for i in range(1, 10):
                flg = len(output.sellContracts) >= i
                data[f"{i}:売約定時間"].append(output.sellContracts[i-1].thatTime.time() if flg else None)
                data[f"{i}:売約定価格"].append(output.sellContracts[i-1].price if flg else None)
                data[f"{i}:売約定直前価格"].append(output.sellContracts[i-1].prevPrice if flg else None)
                data[f"{i}:売約定高値"].append(output.sellContracts[i-1].highPrice if flg else None)
                data[f"{i}:売約定安値"].append(output.sellContracts[i-1].lowPrice if flg else None)
                data[f"{i}:売時VWAP"].append(output.sellContracts[i-1].vwap if flg else None)
                data[f"{i}:売時売買代金"].append(output.sellContracts[i-1].tradingValue if flg else None)
                data[f"{i}:売時売買代金一分"].append(output.sellContracts[i-1].tradingValueByMinute if flg else None)
                data[f"{i}:売時板更新数一分"].append(output.sellContracts[i-1].updateCountByMinute if flg else None)
            pd.DataFrame(data).to_csv(self.csvname, index=False, header=False, mode="a")
