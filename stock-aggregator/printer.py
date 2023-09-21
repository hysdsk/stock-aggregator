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
        self.items = [
            "日付",
            "曜日",
            "銘柄コード",
            "銘柄名",
            "閾値",
            "前日終値",
            "前日時価総額",
            "前場寄前注文時間",
            "前場寄前注文回数",
            "後場寄前注文時間",
            "後場寄前注文回数",
            "寄付時間",
            "寄付価格",
            "寄時売買代金",
            "買前売約定時間",
            "買前売約定価格",
            "買前売約定回数",
            "買約定時間",
            "買約定価格",
            "買約定直前価格",
            "買約定回数",
            "買時売買代金一分",
            "買時板更新数一分",
            "買時売買代金",
            "買時VWAP",
            "買時安値時間",
            "買時安値",
            "買時高値時間",
            "買時高値",
            "買時状態",
            "安値時間",
            "安値",
            "高値時間",
            "高値",
            "VWAP負乖離時間",
            "VWAP負乖離時価格",
            "VWAP負乖離時VWAP",
            "VWAP正乖離時間",
            "VWAP正乖離時価格",
            "VWAP正乖離時VWAP",
            "売約定時間",
            "売約定価格",
            "売約定直前価格",
            "売約定回数",
            "売時売買代金一分",
            "売時板更新数一分",
            "期間内売買代金",
            "売時VWAP",
            "売時状態",
            "売後買約定回数",
            "当日安値時間",
            "当日安値",
            "当日高値時間",
            "当日高値",
            "終了時間",
            "終了価格",
            "当日売買代金",
        ]

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
    def out(self, output: Output):
        pass

    @abstractmethod
    def close(self):
        pass


class ConsolePrinter(Printer):
    def __init__(self):
        super().__init__()
        for i, item in enumerate(self.items):
            print(f"{str(i+1).rjust(2)}. {item}")

    def out(self, output: Output):
        if output.last_message.is_preparing(): return
        tradingvalue = 0
        if output.buy_price is not None:
            tradingvalue = output.last_message.tradingValue - output.buy_tradingvalue

        template = " ".join(["{}"]*len(self.items))
        print(template.format(
            output.last_message.receivedTime.strftime("%Y/%m/%d"),
            self.get_jp_week(output.last_message.receivedTime),
            output.last_message.symbol,
            Formater(output.last_message.symbolName).sname().value,
            Formater(output.threshold).volume().value,
            Formater(output.last_message.previousClose).price().gray().value,
            Formater(output.opening_totalmarketvalue).volume().value,
            str(Formater(output.preparing_m_order_time).time().value).rjust(8),
            str(output.preparing_m_order_count).rjust(2),
            str(Formater(output.resting_m_order_time).time().value).rjust(8),
            str(output.resting_m_order_count).rjust(2),
            Formater(output.last_message.openingPriceTime).time().value,
            Formater(output.last_message.openingPrice).price().green().value,
            Formater(output.opening_tradingvalue).volume().value,
            str(Formater(output.sell_time_before).time().value).rjust(8),
            Formater(output.sell_price_before).price().value,
            str(output.sell_count_before).rjust(2),
            str(Formater(output.buy_time).time().value).rjust(8),
            Formater(output.buy_price).price().value,
            Formater(output.buy_prev_price).price().value,
            str(output.buy_count).rjust(2),
            Formater(output.buy_tradingvalue_byminute).volume().value,
            Formater(output.buy_updatecount_byminute).volume().value,
            Formater(output.buy_tradingvalue).volume().value,
            Formater(round(output.buy_vwap, 0) if output.buy_vwap else None).price().value,
            str(Formater(output.buy_low_price_time).time().value).rjust(8),
            Formater(output.buy_low_price).price().value,
            str(Formater(output.buy_high_price_time).time().value).rjust(8),
            Formater(output.buy_high_price).price().value,
            str(output.buy_status).rjust(9),
            str(Formater(output.low_price_time).time().value).rjust(8),
            Formater(output.low_price).price().value,
            str(Formater(output.high_price_time).time().value).rjust(8),
            Formater(output.high_price).price().value,
            str(Formater(output.low_vwap_diff_time).time().value).rjust(8),
            Formater(output.low_vwap_diff_price + output.low_vwap_diff if output.low_vwap_diff else None).price().value,
            Formater(output.low_vwap_diff_price).price().value,
            str(Formater(output.high_vwap_diff_time).time().value).rjust(8),
            Formater(output.high_vwap_diff_price + output.high_vwap_diff if output.high_vwap_diff else None).price().value,
            Formater(output.high_vwap_diff_price).price().value,
            str(Formater(output.sell_time).time().value).rjust(8),
            Formater(output.sell_price).price().value,
            Formater(output.sell_prev_price).price().value,
            str(output.sell_count).rjust(2),
            Formater(output.sell_tradingvalue_byminute).volume().value,
            Formater(output.sell_updatecount_byminute).volume().value,
            Formater(tradingvalue).volume().value,
            Formater(round(output.sell_vwap, 0) if output.sell_vwap else None).price().value,
            str(output.sell_status).rjust(9),
            str(output.buy_count_after).rjust(2),
            Formater(output.last_message.lowPriceTime).time().value,
            Formater(output.last_message.lowPrice).price().value,
            Formater(output.last_message.highPriceTime).time().value,
            Formater(output.last_message.highPrice).price().value,
            Formater(output.last_message.receivedTime).time().value,
            Formater(output.last_message.currentPrice).price().value,
            Formater(output.last_message.tradingValue).volume().value,
        ))

    def close(self):
        pass


class CsvPrinter(Printer):
    def __init__(self, buyCount: int, sellCount: int):
        super().__init__()
        outdir = self.config["output_directory"][:-1] if self.config["output_directory"][-1] == "/" else self.config["output_directory"]
        self.csvname = f"{outdir}/aggregated_b{buyCount}s{sellCount}.{int(datetime.now().timestamp())}.csv"
        self.writer = open(self.csvname, mode="a", encoding="utf-8")
        for i, item in enumerate(self.items):
            row_end = "\n" if i + 1 >= len(self.items) else ","
            self.writer.write(f"{item}{row_end}")

    def out(self, output: Output):
        if output.last_message.is_preparing(): return
        tradingvalue = None
        if output.buy_tradingvalue is not None:
            tradingvalue = output.last_message.tradingValue - output.buy_tradingvalue

        template = ",".join(["{}"]*len(self.items))
        self.writer.write(f"{template}\n".format(
            output.last_message.receivedTime.strftime("%Y/%m/%d"),
            self.get_jp_week(output.last_message.receivedTime),
            output.last_message.symbol,
            output.last_message.symbolName,
            output.threshold,
            output.last_message.previousClose if output.last_message.previousClose else "",
            output.opening_totalmarketvalue,
            Formater(output.preparing_m_order_time).time().value if output.preparing_m_order_time else "",
            output.preparing_m_order_count,
            Formater(output.resting_m_order_time).time().value if output.resting_m_order_time else "",
            output.resting_m_order_count,
            Formater(output.last_message.openingPriceTime).time().value,
            output.last_message.openingPrice,
            output.opening_tradingvalue,
            Formater(output.sell_time_before).time().value if output.sell_time_before else "",
            output.sell_price_before if output.sell_price_before else "",
            output.sell_count_before,
            Formater(output.buy_time).time().value if output.buy_time else "",
            output.buy_price if output.buy_price else "",
            output.buy_prev_price if output.buy_prev_price else "",
            output.buy_count,
            output.buy_tradingvalue_byminute,
            output.buy_updatecount_byminute,
            output.buy_tradingvalue if output.buy_tradingvalue else "",
            output.buy_vwap if output.buy_vwap else "",
            Formater(output.buy_low_price_time).time().value if output.buy_low_price_time else "",
            output.buy_low_price if output.buy_low_price else "",
            Formater(output.buy_high_price_time).time().value if output.buy_high_price_time else "",
            output.buy_high_price if output.buy_high_price else "",
            output.buy_status if output.buy_status else "",
            Formater(output.low_price_time).time().value if output.low_price_time else "",
            output.low_price if output.low_price else "",
            Formater(output.high_price_time).time().value if output.high_price_time else "",
            output.high_price if output.high_price else "",
            Formater(output.low_vwap_diff_time).time().value if output.low_vwap_diff_time else "",
            output.low_vwap_diff_price + output.low_vwap_diff if output.low_vwap_diff_price else "",
            output.low_vwap_diff_price if output.low_vwap_diff_price else "",
            Formater(output.high_vwap_diff_time).time().value if output.high_vwap_diff_time else "",
            output.high_vwap_diff_price + output.high_vwap_diff if output.high_vwap_diff_price else "",
            output.high_vwap_diff_price if output.high_vwap_diff_price else "",
            Formater(output.sell_time).time().value if output.sell_time else "",
            output.sell_price if output.sell_price else "",
            output.sell_prev_price if output.sell_prev_price else "",
            output.sell_count,
            output.sell_tradingvalue_byminute,
            output.sell_updatecount_byminute,
            tradingvalue if tradingvalue else "",
            output.sell_vwap if output.sell_vwap else "",
            output.sell_status if output.sell_status else "",
            output.buy_count_after,
            Formater(output.last_message.lowPriceTime).time().value,
            output.last_message.lowPrice,
            Formater(output.last_message.highPriceTime).time().value,
            output.last_message.highPrice,
            Formater(output.last_message.receivedTime).time().value,
            output.last_message.currentPrice,
            output.last_message.tradingValue,
        ))

    def close(self):
        self.writer.close()
