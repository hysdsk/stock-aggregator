import json
from datetime import time
from kabustation.message import Message
from .output import Output


class Processor(object):
    def __init__(
            self,
            buy_count: int,
            sell_count: int,
            offset_minute: int,
            close: int,
            thresholds=None) -> None:
        self.buy_count = buy_count
        self.sell_count = sell_count
        self.preparing_time = time(hour=8, minute=60-offset_minute, second=0, microsecond=0)
        self.resting_time = time(hour=12, minute=30-offset_minute, second=0, microsecond=0)
        self.start_time = time(hour=8, minute=0, second=0, microsecond=0)
        self.close_first_time = time(hour=11, minute=30, second=0, microsecond=0)
        self.close_time = time(hour=close, minute=0, second=0, microsecond=0)
        if close == 15:
            self.close_time = time(hour=14, minute=59, second=50, microsecond=0)
        self.thresholds = thresholds

    def _sellorbuy(self, crnt: Message, prev: Message):
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

    def _status(self, crnt: Message, prev: Message) -> str:
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

    def _calc_threshold(self, totalMarketValue: float) -> float:
        if not totalMarketValue:
            return 30000000
        if totalMarketValue >=  65 * (10**9): return round(totalMarketValue * 0.00033)
        if totalMarketValue >=  60 * (10**9): return 20*(10**6)
        if totalMarketValue >=  50 * (10**9): return 19*(10**6)
        if totalMarketValue >=  40 * (10**9): return 18*(10**6)
        if totalMarketValue >=  30 * (10**9): return 17*(10**6)
        if totalMarketValue >=  20 * (10**9): return 16*(10**6)
        if totalMarketValue >=  10 * (10**9): return 15*(10**6)
        return 10000000

    def process(self, messages: list[Message], output: Output) -> int:
        crnt = messages[-1]
        if len(messages) < 2:
            return 0
        prev = messages[-2]
        # 前場寄り前
        if crnt.is_preparing() and crnt.receivedTime.time() >= self.preparing_time:
            value = (crnt.marketOrderBuyQty - prev.marketOrderBuyQty) * crnt.calcPrice
            if value > output.threshold:
                output.preparing_m_order_count += 1
                if output.preparing_m_order_time is None:
                    output.preparing_m_order_time = crnt.receivedTime
            elif -1*value > output.threshold and output.preparing_m_order_count > 0:
                if crnt.askSign == prev.askSign and crnt.bidSign == prev.bidSign:
                    output.preparing_m_order_count -= 1
                    output.preparing_m_order_time = None
        # 寄っていない場合は終了
        if prev.is_preparing():
            if not crnt.is_preparing(): output.opening_tradingvalue = crnt.tradingValue
            return 0
        # 後場寄り前
        if crnt.is_resting() and crnt.receivedTime.time() >= self.resting_time:
            value = (crnt.marketOrderBuyQty - prev.marketOrderBuyQty) * crnt.calcPrice
            if value > output.threshold:
                output.resting_m_order_count += 1
                if output.resting_m_order_time is None:
                    output.resting_m_order_time = crnt.receivedTime
            elif -1*value > output.threshold and output.resting_m_order_count > 0:
                if crnt.askSign == prev.askSign and crnt.bidSign == prev.bidSign:
                    output.resting_m_order_count -= 1
                    output.resting_m_order_time = None
        # 買約定後に売約定出るまで安値と高値を更新する
        if output.buy_count >= self.buy_count and output.sell_count < self.sell_count:
            if output.high_price < crnt.currentPrice:
                output.high_price = crnt.currentPrice
                output.high_price_time = crnt.receivedTime
            if output.low_price > crnt.currentPrice:
                output.low_price = crnt.currentPrice
                output.low_price_time = crnt.receivedTime
        # 閾値で大約定を取得する
        value = crnt.tradingValue - prev.tradingValue
        output.add_lastminutehistories(crnt.receivedTime, value)
        status = self._status(crnt, prev)
        is_close_first = self.close_first_time == crnt.currentPriceTime.time()
        if value >= output.threshold and status == "opening" and not is_close_first:
            sob = self._sellorbuy(crnt, prev)
            if sob > 0:
                if output.sell_count < self.sell_count:
                    output.buy_count += 1
                else:
                    output.buy_count_after += 1
                if output.buy_count >= self.buy_count and output.buy_price is None:
                    output.buy_price = crnt.currentPrice
                    output.buy_prev_price = prev.currentPrice
                    output.buy_time = crnt.currentPriceTime
                    output.buy_vwap = crnt.vwap
                    output.buy_low_price_time = crnt.lowPriceTime
                    output.buy_low_price = crnt.lowPrice
                    output.buy_high_price_time = crnt.highPriceTime
                    output.buy_high_price = crnt.highPrice
                    output.buy_status = self._status(crnt, prev)
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
                if output.sell_count >= self.sell_count and output.sell_price is None:
                    output.sell_price = crnt.currentPrice
                    output.sell_prev_price = prev.currentPrice
                    output.sell_time = crnt.currentPriceTime
                    output.sell_vwap = crnt.vwap
                    output.sell_status = self._status(crnt, prev)
                    output.sell_tradingvalue = crnt.tradingValue
                    output.set_sell_lastminute()
        return 0

    def run(self, lines: list[str]):
        messages: list[Message] = []
        output = Output()
        for line in lines:
            crnt = Message(json.loads(line))
            if crnt.receivedTime.time() < self.start_time:
                continue
            if crnt.receivedTime.time() >= self.close_time:
                break
            if crnt.totalMarketValue is None:
                continue
            if output.opening_totalmarketvalue is None:
                output.opening_totalmarketvalue = crnt.totalMarketValue
                if self.thresholds:
                    output.threshold = self.thresholds[crnt.symbol]
                else:
                    threshold = self._calc_threshold(crnt.totalMarketValue)
                    output.threshold = 50000000 if threshold > 50000000 else threshold
            messages.append(crnt)
            self.process(messages, output)
        output.last_message = messages[-1]
        return output
