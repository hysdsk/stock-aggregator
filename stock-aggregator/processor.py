import json
from datetime import datetime, time, timedelta
from kabustation.message import Message
from .output import Output, Contract, Order


class Processor(object):
    def __init__(
            self,
            offset_minute: int,
            thresholds=None) -> None:
        self.preparing_time = time(hour=8, minute=60-offset_minute)
        self.resting_time = time(hour=12, minute=30-offset_minute)
        self.start_time = time(hour=8, minute=0)
        self.close_time = time(hour=14, minute=59, second=55)
        self.thresholds = thresholds
        self.lastMinuteHistories: list[TradingValueHistory] = []

    def _addLastMinuteHistories(self, receivedtime: datetime, tradingvalue: int):
        self.lastMinuteHistories.append(TradingValueHistory(receivedtime.time(), tradingvalue))
        recenttime = receivedtime - timedelta(minutes=1)
        while self.lastMinuteHistories[0].receivedtime < recenttime.time():
            del self.lastMinuteHistories[0]

    def _sellorbuy(self, crnt: Message, prev: Message):
        prevprice = crnt.previousClose if prev.is_preparing() else prev.currentPrice
        if prevprice:
            if crnt.currentPrice < prevprice:
                return -1
            if crnt.currentPrice > prevprice:
                return 1
            if prev.askPrice and crnt.currentPrice <= prev.askPrice:
                return -1
            if prev.bidPrice and crnt.currentPrice >= prev.bidPrice:
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
        elif not crnt.is_preparing() and crnt.currentPriceTime.time() == time(hour=11, minute=30):
            # 前場引け時
            return "tempbreak"
        else:
            # ザラ場通常時
            return "opening"

    # def _calc_threshold(self, totalMarketValue: float) -> float:
    #     if not totalMarketValue:
    #         return 30000000
    #     if totalMarketValue >=  90 * (10**9): return round(totalMarketValue * 0.00051)
    #     if totalMarketValue >=  80 * (10**9): return 40*(10**6)
    #     if totalMarketValue >=  70 * (10**9): return 36*(10**6)
    #     if totalMarketValue >=  60 * (10**9): return 32*(10**6)
    #     if totalMarketValue >=  50 * (10**9): return 29*(10**6)
    #     if totalMarketValue >=  40 * (10**9): return 28*(10**6)
    #     if totalMarketValue >=  30 * (10**9): return 26*(10**6)
    #     if totalMarketValue >=  20 * (10**9): return 24*(10**6)
    #     if totalMarketValue >=  10 * (10**9): return 22*(10**6)
    #     return                                       20*(10**6)

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
            return
        prev = messages[-2]
        # 前場寄り前
        if crnt.is_preparing() and crnt.receivedTime.time() >= self.preparing_time:
            value = (crnt.marketOrderBuyQty - prev.marketOrderBuyQty) * crnt.calcPrice
            if value > output.threshold:
                output.firstOrders.append(Order(crnt.receivedTime, value))
            elif -1*value > output.threshold and len(output.firstOrders) > 0:
                if crnt.askSign == prev.askSign and crnt.bidSign == prev.bidSign:
                    del output.firstOrders[0]
        # 寄っていない場合は終了
        if prev.is_preparing():
            if not crnt.is_preparing(): output.opening_tradingvalue = crnt.tradingValue
            return
        # 後場寄り前
        if crnt.is_resting() and crnt.receivedTime.time() >= self.resting_time:
            value = (crnt.marketOrderBuyQty - prev.marketOrderBuyQty) * crnt.calcPrice
            if value > output.threshold:
                output.laterOrders.append(Order(crnt.receivedTime, value))
            elif -1*value > output.threshold and len(output.laterOrders) > 0:
                if crnt.askSign == prev.askSign and crnt.bidSign == prev.bidSign:
                    del output.laterOrders[0]
        # 買約定後の安値と高値を更新する
        for buyContract in output.buyContracts:
            buyContract.updateHighAndLow(crnt)
        # 閾値で大約定を取得する
        value = crnt.tradingValue - prev.tradingValue
        self._addLastMinuteHistories(crnt.receivedTime, value)
        status = self._status(crnt, prev)
        if value > 0 and status == "opening":
            sob = self._sellorbuy(crnt, prev)
            # 通常約定
            if sob > 0:
                output.totalBuyCount += 1
                output.totalBuyValue += value
            elif sob < 0:
                output.totalSellCount += 1
                output.totalSellValue += value
            # 大約定
            if value >= output.threshold:
                if sob > 0:
                    output.buyContracts.append(Contract(
                        thatTime=crnt.currentPriceTime,
                        price=crnt.currentPrice,
                        prevPrice=prev.currentPrice,
                        highPrice=prev.highPrice,
                        lowPrice=prev.lowPrice,
                        vwap=crnt.vwap,
                        tradingValue=value,
                        tradingValueByMinute=sum([h.tradingvalue for h in self.lastMinuteHistories]),
                        updateCountByMinute=len(self.lastMinuteHistories)
                    ))
                elif sob < 0:
                    output.sellContracts.append(Contract(
                        thatTime=crnt.currentPriceTime,
                        price=crnt.currentPrice,
                        prevPrice=prev.currentPrice,
                        highPrice=prev.highPrice,
                        lowPrice=prev.lowPrice,
                        vwap=crnt.vwap,
                        tradingValue=value,
                        tradingValueByMinute=sum([h.tradingvalue for h in self.lastMinuteHistories]),
                        updateCountByMinute=len(self.lastMinuteHistories)
                    ))

    def run(self, lines: list[str]) -> Output:
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
                output.threshold = self.thresholds[crnt.symbol] if self.thresholds else self._calc_threshold(crnt.totalMarketValue)
            messages.append(crnt)
            self.process(messages, output)
        output.last_message = messages[-1]
        return output

class TradingValueHistory(object):
    def __init__(self, receivedtime: time, tradingvalue: int):
        self.receivedtime: time = receivedtime
        self.tradingvalue: int = tradingvalue
