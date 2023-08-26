from datetime import datetime
from console import Console, Formater
from kabustation.message import Message


class Printer(Console):
    def __init__(self):
        pass

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

    def out_print(self, message: Message, output: object):
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
