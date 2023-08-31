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
            os.remove(distfile)
            self.writer = open(distfile, mode="a", encoding="utf-8")
            self.writer.write("日付,曜日,銘柄コード,銘柄名,初回買大約定時間,初回買大約定価格,買大約定数,初回売大約定時間（終了時含む）,初回売大約定価格（終了時含む）,売大約定数,価格騰落率")
            if self.item == "full":
                print("test")
                self.writer.write(",売買代金,高値,安値")
            self.writer.write("\n")
        else:
            print(" 1. 日付")
            print(" 2. 銘柄コード")
            print(" 3. 銘柄名")
            print(" 4. 初回買大約定時間")
            print(" 5. 初回買大約定価格")
            print(" 6. 買大約定数")
            print(" 7. 初回売大約定時間（終了時含む）")
            print(" 8. 初回売大約定価格（終了時含む）")
            print(" 9. 売大約定数")
            print("10. 価格騰落率")
            if self.item == "full":
                print("11. 売買代金")
                print("12. 高値")
                print("13. 安値")

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

    def out_console(self, message: Message, output: Output):
        rate = round((output.out_price / output.buy_price * 100) - 100, 2)
        tradingvalue = message.tradingValue - output.buy_tradingvalue

        content = "{}({}) {} {} {} {} {} {} {} {} {}".format(
            message.receivedTime.strftime("%Y/%m/%d"),
            self.get_jp_week(message.receivedTime),
            message.symbol,
            Formater(message.symbolName).sname().value,
            Formater(output.buy_time).time().value,
            Formater(output.buy_price).price().value,
            str(output.buy_count).rjust(2),
            Formater(output.out_time).time().value,
            Formater(output.out_price).price().value,
            str(output.sell_count).rjust(2),
            super().formatrate(rate))

        if self.item == "full":
            content = "{} {} {} {}".format(
                content,
                Formater(tradingvalue).volume().value,
                Formater(output.high_price).price().value,
                Formater(output.low_price).price().value)

        self.print(content)

    def out_csv(self, message: Message, output: Output):
        rate = round((output.out_price / output.buy_price * 100) - 100, 2)
        tradingvalue = message.tradingValue - output.buy_tradingvalue

        content = "{},{},{},{},{},{},{},{},{},{},{}".format(
            message.receivedTime.strftime("%Y/%m/%d"),
            self.get_jp_week(message.receivedTime),
            message.symbol,
            message.symbolName,
            Formater(output.buy_time).time().value,
            Formater(output.buy_price).price().value,
            output.buy_count,
            Formater(output.out_time).time().value,
            Formater(output.out_price).price().value,
            output.sell_count,
            rate)

        if self.item == "full":
            content = "{},{},{},{}".format(
                content,
                tradingvalue,
                Formater(output.high_price).price().value,
                Formater(output.low_price).price().value)

        self.writer.write(f"{content}\n")

    def close_writer(self):
        if hasattr(self, "writer") and self.writer:
            self.writer.close()
