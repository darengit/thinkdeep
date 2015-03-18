import sys

from utils.db import local_pymysql_conn, load_all_ohlc
from utils.ohlc import OHLC
from utils.ohlc_transition import OHLCTransition
from utils.hl_transition import HLTransition


tablename = sys.argv[1]
transition = eval(sys.argv[2])
lookback = int(sys.argv[3])

conn = local_pymysql_conn()
(dates, opens, highs, lows, closes) = load_all_ohlc(conn, tablename)

ohlc_transitions = []
ohlc_prev = None

for (date, o, h, l, c) in zip(dates, opens, highs, lows, closes):
    ohlc = OHLC(date, o, h, l, c)

    if ohlc_prev is not None:
        ohlc_transitions.append(transition(ohlc_prev, ohlc))

    ohlc_prev = ohlc

for starting_idx in range(0,len(ohlc_transitions)-lookback+1):
    match = True
    for idx_offset in range(0, lookback):
        if ohlc_transitions[starting_idx+idx_offset] != ohlc_transitions[len(ohlc_transitions)-lookback+idx_offset]:
            match = False
            break
    if match:
        print("{0:%Y-%m-%d}".format(ohlc_transitions[starting_idx+lookback-1].date))
