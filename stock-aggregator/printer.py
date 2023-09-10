from datetime import datetime
from console import Console, Formater
from kabustation.message import Message
from .output import Output


class Printer(Console):
    def __init__(self, distfile=None):
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
            "買約定回数",
            "買時売買代金",
            "買時VWAP",
            "買時状態",
            "安値時間",
            "安値",
            "高値時間",
            "高値",
            "売約定時間",
            "売約定価格",
            "売約定回数",
            "売時状態",
            "期間内売買代金",
            "売後買約定回数",
            "当日安値時間",
            "当日安値",
            "当日高値時間",
            "当日高値",
            "終了時間",
            "終了価格",
            "当日売買代金",
        ]
        if distfile:
            self.writer = open(distfile, mode="a", encoding="utf-8")
            for i, item in enumerate(self.items):
                row_end = "\n" if i + 1 >= len(self.items) else ","
                self.writer.write(f"{item}{row_end}")
        else:
            num = 0
            for i, item in enumerate(self.items):
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

    def out_console(self, message: Message, output: Output, threshold: int, openingTotalMarketValue: float):
        if message.is_preparing(): return
        tradingvalue = 0
        if output.buy_price is not None:
            tradingvalue = message.tradingValue - output.buy_tradingvalue

        template = " ".join(["{}"]*len(self.items))
        self.print(template.format(
            message.receivedTime.strftime("%Y/%m/%d"),
            self.get_jp_week(message.receivedTime),
            message.symbol,
            Formater(message.symbolName).sname().value,
            Formater(threshold).volume().value,
            Formater(message.previousClose).price().gray().value,
            Formater(openingTotalMarketValue).volume().value,
            str(Formater(output.preparing_m_order_time).time().value).rjust(8),
            str(output.preparing_m_order_count).rjust(2),
            str(Formater(output.resting_m_order_time).time().value).rjust(8),
            str(output.resting_m_order_count).rjust(2),
            Formater(message.openingPriceTime).time().value,
            Formater(message.openingPrice).price().green().value,
            Formater(output.opening_tradingvalue).volume().value,
            str(Formater(output.sell_time_before).time().value).rjust(8),
            Formater(output.sell_price_before).price().value,
            str(output.sell_count_before).rjust(2),
            str(Formater(output.buy_time).time().value).rjust(8),
            Formater(output.buy_price).price().value,
            str(output.buy_count).rjust(2),
            Formater(output.buy_tradingvalue).volume().value,
            Formater(round(output.buy_vwap, 0) if output.buy_vwap else None).price().value,
            str(output.buy_status).rjust(9),
            str(Formater(output.low_price_time).time().value).rjust(8),
            Formater(output.low_price).price().value,
            str(Formater(output.high_price_time).time().value).rjust(8),
            Formater(output.high_price).price().value,
            str(Formater(output.sell_time).time().value).rjust(8),
            Formater(output.sell_price).price().value,
            str(output.sell_count).rjust(2),
            str(output.sell_status).rjust(9),
            Formater(tradingvalue).volume().value,
            str(output.buy_count_after).rjust(2),
            Formater(message.lowPriceTime).time().value,
            Formater(message.lowPrice).price().value,
            Formater(message.highPriceTime).time().value,
            Formater(message.highPrice).price().value,
            Formater(message.receivedTime).time().value,
            Formater(message.currentPrice).price().value,
            Formater(message.tradingValue).volume().value,
        ))

    def out_csv(self, message: Message, output: Output, threshold: int, openingTotalMarketValue: float):
        if message.is_preparing(): return
        tradingvalue = 0
        if output.buy_price is not None:
            tradingvalue = message.tradingValue - output.buy_tradingvalue

        template = ",".join(["{}"]*len(self.items))
        self.writer.write(f"{template}\n".format(
            message.receivedTime.strftime("%Y/%m/%d"),
            self.get_jp_week(message.receivedTime),
            message.symbol,
            message.symbolName,
            threshold,
            0 if message.previousClose is None else message.previousClose,
            openingTotalMarketValue,
            Formater(output.preparing_m_order_time).time().value,
            output.preparing_m_order_count,
            Formater(output.resting_m_order_time).time().value,
            output.resting_m_order_count,
            Formater(message.openingPriceTime).time().value,
            message.openingPrice,
            output.opening_tradingvalue,
            Formater(output.sell_time_before).time().value,
            output.sell_price_before,
            output.sell_count_before,
            Formater(output.buy_time).time().value,
            output.buy_price,
            output.buy_count,
            output.buy_tradingvalue,
            output.buy_vwap,
            output.buy_status,
            Formater(output.low_price_time).time().value,
            output.low_price,
            Formater(output.high_price_time).time().value,
            output.high_price,
            Formater(output.sell_time).time().value,
            output.sell_price,
            output.sell_count,
            output.sell_status,
            tradingvalue,
            output.buy_count_after,
            Formater(message.lowPriceTime).time().value,
            message.lowPrice,
            Formater(message.highPriceTime).time().value,
            message.highPrice,
            Formater(message.receivedTime).time().value,
            message.currentPrice,
            message.tradingValue,
            ))

    def close_writer(self):
        if hasattr(self, "writer") and self.writer:
            self.writer.close()
