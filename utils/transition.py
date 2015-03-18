class Transition:
    def __init__(self, ohlc_prev, ohlc):
        self.date_prev = ohlc_prev.date
        self.date = ohlc.date

    def __eq__(self, other):
        return False

