import os
from datetime import datetime
from console import Console, Formater
from kabustation.message import Message
from .output import Output


class Printer(Console):
    def __init__(self,
                 item_len="short",
                 distfile=None):
        self.item_len = item_len
        self.items = [
            "日付",       # 1
            "曜日",       # 2
            "銘柄コード", # 3
            "銘柄名",     # 4
            "閾値",       # 5
            "前日終値",   # 6 -
            "始値時間",   # 7 -
            "当日始値",   # 8 -
            "始値終値比", # 9 -
            "買約定時間", # 10
            "買約定価格", # 11
            "買値始値比", # 12 -
            "買値VWAP比", # 13 -
            "安値時間",   # 14 -
            "安値",       # 15 -
            "安値買値比", # 16 -
            "高値時間",   # 17 -
            "高値",       # 18 -
            "高値買値比", # 19 -
            "買約定回数", # 20
            "売約定回数", # 21
            "終了時間",   # 22
            "終了価格",   # 23
            "終了買値比", # 24
            "売買代金",   # 25 -
        ]
        if distfile:
            if os.path.exists(distfile):
                os.remove(distfile)
            self.writer = open(distfile, mode="a", encoding="utf-8")
            for i, item in enumerate(self.items):
                row_end = "\n" if i + 1 >= len(self.items) else ","
                self.writer.write(f"{item}{row_end}")
        else:
            num = 0
            for i, item in enumerate(self.items):
                if self.item_len != "full" and i + 1 not in [1, 2, 3, 4, 5, 10, 11, 20, 21, 22, 23, 24]:
                    continue
                num += 1
                print(f"{str(num).rjust(2)}. {item}")

    def print(self, content: str):
        super().print(content)

    def get_jp_week(self, thatday: datetime):
        num = thatday.weekday()
        if num == 0: return "月"
        if num == 1: return "火"
        if num == 2: return "水"
        if num == 3: return "木"
        if num == 4: return "金"
        if num == 5: return "土"
        return "日"

    def out_console(self, message: Message, output: Output, threshold: int):
        a = ""
        b = ""
        c = ""
        if self.item_len == "full":
            opening_closing_rate = 0
            if message.previousClose is not None:
                opening_closing_rate = round((message.openingPrice / message.previousClose * 100) - 100, 2)
            buy_opening_rate = round((output.buy_price / message.openingPrice * 100) - 100, 2)
            buy_vwap_rate = round((output.buy_price / output.buy_vwap * 100) - 100, 2)
            low_buy_rate = round((output.low_price / output.buy_price * 100) - 100, 2)
            high_buy_rate = round((output.high_price / output.buy_price * 100) - 100, 2)
            tradingvalue = message.tradingValue - output.buy_tradingvalue
            a = " {} {} {} {}".format(
                Formater(message.previousClose).price().gray().value,
                Formater(message.openingPriceTime).time().value,
                Formater(message.openingPrice).price().green().value,
                super().formatrate(opening_closing_rate))
            b = " {} {} {} {} {} {} {} {}". format(
                super().formatrate(buy_opening_rate),
                super().formatrate(buy_vwap_rate),
                Formater(output.low_price_time).time().value,
                Formater(output.low_price).price().value,
                super().formatrate(low_buy_rate),
                Formater(output.high_price_time).time().value,
                Formater(output.high_price).price().value,
                super().formatrate(high_buy_rate))
            c = Formater(tradingvalue).volume().value

        close_buy_rate = round((output.out_price / output.buy_price * 100) - 100, 2)
        self.print("{}({}) {} {} {} {} {} {} {} {} {} {} {} {} {}".format(
            message.receivedTime.strftime("%Y/%m/%d"),
            self.get_jp_week(message.receivedTime),
            message.symbol,
            Formater(message.symbolName).sname().value,
            Formater(threshold).volume().value,
            a,
            Formater(output.buy_time).time().value,
            Formater(output.buy_price).price().value,
            b,
            str(output.buy_count).rjust(2),
            str(output.sell_count).rjust(2),
            Formater(output.out_time).time().value,
            Formater(output.out_price).price().value,
            super().formatrate(close_buy_rate),
            c))

    def out_csv(self, message: Message, output: Output, threshold: int):
        close_buy_rate = round((output.out_price / output.buy_price * 100) - 100, 2)
        buy_opening_rate = round((output.buy_price / message.openingPrice * 100) - 100, 2)
        buy_vwap_rate = round((output.buy_price / output.buy_vwap * 100) - 100, 2)
        low_buy_rate = round((output.low_price / output.buy_price * 100) - 100, 2)
        high_buy_rate = round((output.high_price / output.buy_price * 100) - 100, 2)
        opening_closing_rate = 0
        if message.previousClose is not None:
            opening_closing_rate = round((message.openingPrice / message.previousClose * 100) - 100, 2)
        tradingvalue = message.tradingValue - output.buy_tradingvalue

        self.writer.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
            message.receivedTime.strftime("%Y/%m/%d"),
            self.get_jp_week(message.receivedTime),
            message.symbol,
            message.symbolName,
            threshold,
            0 if message.previousClose is None else message.previousClose,
            Formater(message.openingPriceTime).time().value,
            message.openingPrice,
            opening_closing_rate,
            Formater(output.buy_time).time().value,
            output.buy_price,
            buy_opening_rate,
            buy_vwap_rate,
            Formater(output.low_price_time).time().value,
            output.low_price,
            low_buy_rate,
            Formater(output.high_price_time).time().value,
            output.high_price,
            high_buy_rate,
            output.buy_count,
            output.sell_count,
            Formater(output.out_time).time().value,
            output.out_price,
            close_buy_rate,
            tradingvalue))

    def close_writer(self):
        if hasattr(self, "writer") and self.writer:
            self.writer.close()
