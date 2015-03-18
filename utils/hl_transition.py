from utils.transition import Transition

class HLTransition(Transition):
    def __init__(self, ohlc_prev, ohlc):
        super(HLTransition, self).__init__(ohlc_prev, ohlc)

        self.high_transition = 0 if ohlc.h < ohlc_prev.h else 1
        self.low_transition = 0 if ohlc.l < ohlc_prev.l else 1

    def __eq__(self, other):
        return self.high_transition == other.high_transition and\
               self.low_transition == other.low_transition

