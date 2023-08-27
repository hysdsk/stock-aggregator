import os
from datetime import datetime
from console import Console, Formater
from kabustation.message import Message


class Printer(Console):
    def __init__(self, distfile=None):
        if distfile:
            os.remove(distfile)
            self.writer = open(distfile, mode="a", encoding="utf-8")
            self.writer.write("日付,曜日,銘柄コード,銘柄名,初回買大約定時間,初回買大約定価格,買大約定数,初回売大約定時間（終了時含む）,初回売大約定価格（終了時含む）,価格騰落率\n")

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

    def out_console(self, message: Message, output: object):
        rate = round((output["out_price"] / output["buy_price"] * 100) - 100, 2)

        content = "{}({}) {} {} {} {} {} {} {} {}".format(
            message.receivedTime.strftime("%Y/%m/%d"),
            self.get_jp_week(message.receivedTime),
            message.symbol,
            Formater(message.symbolName).sname().value,
            Formater(output["buy_time"]).time().value,
            Formater(output["buy_price"]).price().value,
            output["buy_count"],
            Formater(output["out_time"]).time().value,
            Formater(output["out_price"]).price().value,
            super().formatrate(rate))

        self.print(content)

    def out_csv(self, message: Message, output: object):
        rate = round((output["out_price"] / output["buy_price"] * 100) - 100, 2)

        content = "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}\n".format(
            message.receivedTime.strftime("%Y/%m/%d"),
            self.get_jp_week(message.receivedTime),
            message.symbol,
            message.symbolName,
            Formater(output["buy_time"]).time().value,
            Formater(output["buy_price"]).price().value,
            output["buy_count"],
            Formater(output["out_time"]).time().value,
            Formater(output["out_price"]).price().value,
            rate)

        self.writer.write(content)

    def close_writer(self):
        if hasattr(self, "writer") and self.writer:
            self.writer.close()
