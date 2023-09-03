from abc import abstractmethod
from datetime import datetime
from kabustation.message import Message
from .output import Output


class Processor(object):
    def __init__(self, thresholds: object, buy: int, sell: int) -> None:
        self.thresholds = thresholds
        self.buy = buy
        self.sell = sell
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
    @abstractmethod
    def run(self, messages: list[Message], output: Output) -> int:
        pass

class ContractProcessor(Processor):
    def __init__(self, thresholds: object, buy: int, sell: int) -> None:
        super().__init__(thresholds, buy, sell)
    def run(self, messages: list[Message], output: Output) -> int:
        crnt = messages[-1]
        if len(messages) < 2:
            return 0
        prev = messages[-2]
        if prev.currentPrice is None:
            return 0

        if output.buy_price is not None:
            if output.high_price < crnt.currentPrice:
                output.high_price = crnt.currentPrice
            if output.low_price > crnt.currentPrice:
                output.low_price = crnt.currentPrice

        value = crnt.tradingValue - prev.tradingValue
        if value > self.thresholds[crnt.symbol]:
            sob = super().sellorbuy(crnt, prev)
            if sob > 0:
                output.buy_count += 1
                if output.buy_count >= self.buy and output.buy_price is None:
                    output.buy_price = crnt.currentPrice
                    output.buy_time = crnt.currentPriceTime
                    output.buy_tradingvalue = crnt.tradingValue
                    output.high_price = crnt.currentPrice
                    output.low_price = crnt.currentPrice
            elif sob < 0:
                output.sell_count += 1
                if output.sell_count >= self.sell:
                   return 1
        return 0

class OrderProcessor(Processor):
    def __init__(self, thresholds: object, buy: int, sell: int, offset_minute: int) -> None:
        super().__init__(thresholds, buy, sell)
        self.time0855 = datetime.now().replace(hour=8, minute=60-offset_minute, second=0, microsecond=0)
        self.time1130 = datetime.now().replace(hour=11, minute=30, second=0, microsecond=0)
        self.time1225 = datetime.now().replace(hour=12, minute=30-offset_minute, second=0, microsecond=0)
    def is_skip(self, currenttime: datetime):
        return currenttime.time() < self.time0855.time() or \
            (currenttime.time() >= self.time1130.time() and currenttime.time() < self.time1225.time())
    def run(self, messages: list[Message], output: Output) -> int:
        crnt = messages[-1]
        if len(messages) < 2:
            return 0
        if self.is_skip(crnt.receivedTime):
            return 0

        prev = messages[-2]
        if output.buy_count >= self.buy:
            if output.buy_time is None:
                output.buy_time = crnt.receivedTime
            if output.buy_price is None and crnt.is_opening():
                output.buy_price = crnt.currentPrice
                output.high_price = crnt.currentPrice
                output.low_price = crnt.currentPrice
                output.buy_tradingvalue = crnt.tradingValue
            if output.buy_price is not None:
                if output.high_price < crnt.currentPrice:
                    output.high_price = crnt.currentPrice
                if output.low_price > crnt.currentPrice:
                    output.low_price = crnt.currentPrice

        if crnt.is_opening() and prev.is_opening():
            value = crnt.tradingValue - prev.tradingValue
            sob = super().sellorbuy(crnt, prev)
            if value > self.thresholds[crnt.symbol] and sob < 0:
                output.sell_count += 1
                if output.sell_count >= self.sell:
                   return 1
        if not crnt.is_opening():
            value = (crnt.marketOrderBuyQty - prev.marketOrderBuyQty) * crnt.calcPrice
            if value > self.thresholds[crnt.symbol]:
                output.buy_count += 1
            elif value * -1 > self.thresholds[crnt.symbol] and output.buy_count > 0:
                if crnt.askSign == prev.askSign and crnt.bidSign == prev.bidSign:
                    output.buy_count -= 1
                    output.buy_time = None
        return 0
