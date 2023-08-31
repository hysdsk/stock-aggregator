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
