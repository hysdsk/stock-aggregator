from datetime import datetime
from kabustation.message import Message
from .output import Output


class Processor(object):
    def __init__(
            self,
            threshold: int,
            buy_count: int,
            sell_count: int,
            offset_minute: int) -> None:
        self.threshold = threshold
        self.buy_count = buy_count
        self.sell_count = sell_count
        self.preparing_time = datetime.now().replace(hour=8, minute=60-offset_minute, second=0, microsecond=0)
        self.resting_time = datetime.now().replace(hour=12, minute=30-offset_minute, second=0, microsecond=0)
    def sellorbuy(self, crnt: Message, prev: Message):
        prevprice = crnt.previousClose if prev.is_preparing() else prev.currentPrice
        if prevprice:
            if crnt.currentPrice < prevprice:
                return -1
            if crnt.currentPrice > prevprice:
                return 1
            if prev.askPrice and prevprice <= prev.askPrice:
                return -1
            if prev.bidPrice and prevprice >= prev.bidPrice:
                return 1
        return 0
    def status(self, crnt: Message, prev: Message) -> str:
        if crnt.is_preparing():
            # 前場寄り前
            return "preparing"
        elif not crnt.is_preparing() and prev.is_preparing():
            # 前場寄り時
            return "nowopened"
        elif prev.is_resting() and crnt.tradingVolume > prev.tradingVolume:
            # 後場寄り時
            return "reopened"
        elif prev.is_freezing() and crnt.tradingVolume > prev.tradingVolume:
            # 連特寄り時
            return "resumed"
        elif crnt.is_resting() and crnt.tradingVolume == prev.tradingVolume:
            # 休憩（前場後場間）
            return "resting"
        elif crnt.is_freezing() and crnt.tradingVolume == prev.tradingVolume:
            # 連続・特別気配時
            return "freezing"
        elif crnt.is_closing():
            # 後場引け時
            return "closing"
        else:
            # ザラ場通常時
            return "opening"

    def run(self, messages: list[Message], output: Output) -> int:
        crnt = messages[-1]
        if len(messages) < 2:
            return 0
        prev = messages[-2]
        if crnt.is_preparing() and crnt.receivedTime.time() >= self.preparing_time.time():
            value = (crnt.marketOrderBuyQty - prev.marketOrderBuyQty) * crnt.calcPrice
            if value > self.threshold:
                output.preparing_m_order_count += 1
                if output.preparing_m_order_time is None:
                    output.preparing_m_order_time = crnt.receivedTime
            elif -1*value > self.threshold and output.preparing_m_order_count > 0:
                if crnt.askSign == prev.askSign and crnt.bidSign == prev.bidSign:
                    output.preparing_m_order_count -= 1
                    output.preparing_m_order_time = None
        if crnt.is_resting() and crnt.receivedTime.time() >= self.resting_time.time():
            value = (crnt.marketOrderBuyQty - prev.marketOrderBuyQty) * crnt.calcPrice
            if value > self.threshold:
                output.resting_m_order_count += 1
                if output.resting_m_order_time is None:
                    output.resting_m_order_time = crnt.receivedTime
            elif -1*value > self.threshold and output.resting_m_order_count > 0:
                if crnt.askSign == prev.askSign and crnt.bidSign == prev.bidSign:
                    output.resting_m_order_count -= 1
                    output.resting_m_order_time = None

        if prev.is_preparing():
            if not crnt.is_preparing(): output.opening_tradingvalue = crnt.tradingValue
            return 0

        if output.buy_count >= self.buy_count and output.sell_count < self.sell_count:
            if output.high_price < crnt.currentPrice:
                output.high_price = crnt.currentPrice
                output.high_price_time = crnt.receivedTime
            if output.low_price > crnt.currentPrice:
                output.low_price = crnt.currentPrice
                output.low_price_time = crnt.receivedTime

        value = crnt.tradingValue - prev.tradingValue
        output.add_lastminutehistories(crnt.receivedTime, value)
        if value > self.threshold:
            sob = self.sellorbuy(crnt, prev)
            if sob > 0:
                if output.sell_count < self.sell_count:
                    output.buy_count += 1
                else:
                    output.buy_count_after += 1
                if output.buy_count >= self.buy_count and output.buy_price is None:
                    output.buy_price = crnt.currentPrice
                    output.buy_time = crnt.currentPriceTime
                    output.buy_vwap = crnt.vwap
                    output.buy_status = self.status(crnt, prev)
                    output.buy_tradingvalue = crnt.tradingValue
                    output.set_buy_lastminute()
                    if output.sell_count < self.sell_count:
                        output.high_price = crnt.currentPrice
                        output.high_price_time = crnt.receivedTime
                        output.low_price = crnt.currentPrice
                        output.low_price_time = crnt.receivedTime
            elif sob < 0:
                if output.buy_count >= self.buy_count:
                    output.sell_count += 1
                else:
                    output.sell_count_before += 1
                    if output.sell_price_before is None:
                        output.sell_price_before = crnt.currentPrice
                        output.sell_time_before = crnt.receivedTime
                        output.set_sell_lastminute()
                if output.sell_count >= self.sell_count and output.sell_price is None:
                    output.sell_price = crnt.currentPrice
                    output.sell_time = crnt.currentPriceTime
                    output.sell_vwap = crnt.vwap
                    output.sell_status = self.status(crnt, prev)
                    output.sell_tradingvalue = crnt.tradingValue
        return 0
