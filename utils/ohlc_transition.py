class OHLCTransition:
    def __init__(self, ohlc_prev, ohlc):
        self.date_prev = ohlc_prev.date
        self.date = ohlc.date

        self.bullish_intra_day_swing = 0 if (ohlc_prev.c-ohlc.l) > (ohlc.h-ohlc_prev.c) else 1
        self.bullish_close = 0 if ohlc.c < ohlc_prev.c else 1

    def __eq__(self, other):
        return self.bullish_intra_day_swing == other.bullish_intra_day_swing and\
               self.bullish_close == other.bullish_close

