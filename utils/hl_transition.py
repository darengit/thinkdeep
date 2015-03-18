class HLTransition:
    def __init__(self, ohlc_before, ohlc_after):
        self.date_before = ohlc_before.date
        self.date_after = ohlc_after.date

        self.high_transition = 0 if ohlc_after.h < ohlc_before.h else 1
        self.low_transition = 0 if ohlc_after.l < ohlc_before.l else 1

    def __eq__(self, other):
        return self.high_transition == other.high_transition and\
               self.low_transition == other.low_transition

