class Output(object):
    def __init__(self) -> None:
        self.buy_price = None
        self.buy_time = None
        self.buy_vwap = None
        self.buy_count = 0
        self.buy_count_after = 0
        self.buy_status = None
        self.buy_tradingvalue = 0
        self.sell_price = None
        self.sell_time = None
        self.sell_vwap = None
        self.sell_count = 0
        self.sell_price_before = None
        self.sell_time_before = None
        self.sell_count_before = 0
        self.sell_status = None
        self.sell_tradingvalue = 0
        self.high_price = None
        self.low_price = None
        self.high_price_time = None
        self.low_price_time = None
        self.opening_tradingvalue = None
        self.preparing_m_order_time = None
        self.preparing_m_order_count = 0
        self.resting_m_order_time = None
        self.resting_m_order_count = 0
