from datetime import datetime

class Contract(object):
    def __init__(self,
                thatTime,
                price,
                prevPrice,
                vwap,
                tradingValue,
                tradingValueByMinute,
                updateCountByMinute) -> None:
        self.thatTime: datetime = thatTime
        self.price = price
        self.prevPrice = prevPrice
        self.vwap = vwap
        self.tradingValue = tradingValue
        self.tradingValueByMinute = tradingValueByMinute
        self.updateCountByMinute = updateCountByMinute

class Order(object):
    def __init__(self, thatTime, orderValue) -> None:
        self.thatTime: datetime = thatTime
        self.orderValue = orderValue

class Output(object):
    def __init__(self) -> None:
        self.buyContracts: list[Contract] = []
        self.sellContracts: list[Contract] = []
        self.firstOrders: list[Order] = []
        self.laterOrders: list[Order] = []
        self.high_price_time = None
        self.high_price = None
        self.low_price_time = None
        self.low_price = None
        self.opening_tradingvalue = None
        self.last_message = None
        self.threshold = None
        self.opening_totalmarketvalue = None
