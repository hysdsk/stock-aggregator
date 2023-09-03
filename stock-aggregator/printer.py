import os
from datetime import datetime
from console import Console, Formater
from kabustation.message import Message
from .output import Output


class Printer(Console):
    def __init__(self,
                 item="short",
                 distfile=None):
        self.item = item
        if distfile:
            if os.path.exists(distfile):
                os.remove(distfile)
            self.writer = open(distfile, mode="a", encoding="utf-8")
            self.writer.write("日付,曜日,銘柄コード,銘柄名,閾値,初回買大約定時間,初回買大約定価格,買大約定数,初回売大約定時間（終了時含む）,初回売大約定価格（終了時含む）,売大約定数,価格騰落率")
            if self.item == "full":
                self.writer.write(",売買代金,高値,安値,寄り時間,ギャップ率")
            self.writer.write("\n")
        else:
            print(" 1. 日付")
            print(" 2. 銘柄コード")
            print(" 3. 銘柄名")
            print(" 4. 閾値")
            print(" 5. 初回買大約定時間")
            print(" 6. 初回買大約定価格")
            print(" 7. 買大約定数")
            print(" 8. 初回売大約定時間（終了時含む）")
            print(" 9. 初回売大約定価格（終了時含む）")
            print("10. 売大約定数")
            print("11. 価格騰落率")
            if self.item == "full":
                print("12. 売買代金")
                print("13. 高値")
                print("14. 安値")
                print("15. 寄り時間")
                print("16. ギャップ率")

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
        rate = round((output.out_price / output.buy_price * 100) - 100, 2)
        tradingvalue = message.tradingValue - output.buy_tradingvalue

        content = "{}({}) {} {} {} {} {} {} {} {} {} {}".format(
            message.receivedTime.strftime("%Y/%m/%d"),
            self.get_jp_week(message.receivedTime),
            message.symbol,
            Formater(message.symbolName).sname().value,
            Formater(threshold).volume().value,
            Formater(output.buy_time).time().value,
            Formater(output.buy_price).price().value,
            str(output.buy_count).rjust(2),
            Formater(output.out_time).time().value,
            Formater(output.out_price).price().value,
            str(output.sell_count).rjust(2),
            super().formatrate(rate))

        if self.item == "full":
            openingrate = 0
            if message.previousClose is not None:
                openingrate = round((message.openingPrice / message.previousClose * 100) - 100, 2)
            content = "{} {} {} {} {} {}".format(
                content,
                Formater(tradingvalue).volume().value,
                Formater(output.high_price).price().value,
                Formater(output.low_price).price().value,
                Formater(message.openingPriceTime).time().value,
                super().formatrate(openingrate))

        self.print(content)

    def out_csv(self, message: Message, output: Output, threshold: int):
        rate = round((output.out_price / output.buy_price * 100) - 100, 2)
        tradingvalue = message.tradingValue - output.buy_tradingvalue

        content = "{},{},{},{},{},{},{},{},{},{},{},{}".format(
            message.receivedTime.strftime("%Y/%m/%d"),
            self.get_jp_week(message.receivedTime),
            message.symbol,
            message.symbolName,
            threshold,
            Formater(output.buy_time).time().value,
            output.buy_price,
            output.buy_count,
            Formater(output.out_time).time().value,
            output.out_price,
            output.sell_count,
            rate)

        if self.item == "full":
            openingrate = 0
            if message.previousClose is not None:
                openingrate = round((message.openingPrice / message.previousClose * 100) - 100, 2)
            content = "{},{},{},{},{},{}".format(
                content,
                tradingvalue,
                output.high_price,
                output.low_price,
                Formater(message.openingPriceTime).time().value,
                openingrate)

        self.writer.write(f"{content}\n")

    def close_writer(self):
        if hasattr(self, "writer") and self.writer:
            self.writer.close()
