from datetime import datetime, time, timedelta


class Output(object):
    def __init__(self) -> None:
        self.lastminutehistories: list[TradingValueHistory] = []
        self.buy_price = None
        self.buy_prev_price = None
        self.buy_time = None
        self.buy_vwap = None
        self.buy_low_price = None
        self.buy_low_price_time = None
        self.buy_high_price = None
        self.buy_high_price_time = None
        self.buy_count = 0
        self.buy_count_after = 0
        self.buy_status = None
        self.buy_tradingvalue = None
        self.buy_tradingvalue_byminute = 0
        self.buy_updatecount_byminute = 0
        self.sell_price = None
        self.sell_prev_price = None
        self.sell_time = None
        self.sell_vwap = None
        self.sell_count = 0
        self.sell_price_before = None
        self.sell_time_before = None
        self.sell_count_before = 0
        self.sell_status = None
        self.sell_tradingvalue = None
        self.sell_tradingvalue_byminute = 0
        self.sell_updatecount_byminute = 0
        self.high_price = None
        self.low_price = None
        self.high_price_time = None
        self.low_price_time = None
        self.opening_tradingvalue = None
        self.preparing_m_order_time = None
        self.preparing_m_order_count = 0
        self.resting_m_order_time = None
        self.resting_m_order_count = 0
        self.last_message = None
        self.threshold = None
        self.opening_totalmarketvalue = None

    def set_buy_lastminute(self):
        self.buy_tradingvalue_byminute = self.tradingvalue_byminute()
        self.buy_updatecount_byminute = self.updatecount_byminute()

    def set_sell_lastminute(self):
        self.sell_tradingvalue_byminute = self.tradingvalue_byminute()
        self.sell_updatecount_byminute = self.updatecount_byminute()

    def add_lastminutehistories(self, receivedtime: datetime, tradingvalue: int):
        self.lastminutehistories.append(TradingValueHistory(receivedtime.time(), tradingvalue))
        recenttime = receivedtime - timedelta(minutes=1)
        while self.lastminutehistories[0].receivedtime < recenttime.time():
            del self.lastminutehistories[0]

    def tradingvalue_byminute(self):
        return sum([h.tradingvalue for h in self.lastminutehistories])
    
    def updatecount_byminute(self):
        return len(self.lastminutehistories)

class TradingValueHistory(object):
    def __init__(self, receivedtime: time, tradingvalue: int):
        self.receivedtime: time = receivedtime
        self.tradingvalue: int = tradingvalue
