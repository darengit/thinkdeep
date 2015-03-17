import urllib.request
import datetime
import os
import sys
import numpy

lookback = int(sys.argv[1])

today = datetime.date.today()

url = "http://ichart.finance.yahoo.com/table.csv?s=%5EGSPC&d=" + str(today.month - 1) + "&e=" + str(today.day) + "&f=" + str(today.year) + "&g=d&a=0&b=3&c=1950&ignore=.csv"
response = urllib.request.urlopen(url)

raw_data = list(response)
#print(raw_data)
raw_data.pop(0)
raw_data.reverse()

if len(sys.argv) >= 3:
    raw_data.append(sys.argv[2].encode("utf-8"))

class OHLC:
    def __init__(self, date, o, h, l, c):
        self.date = date
        self.o = o
        self.h = h
        self.l = l
        self.c = c


class OHLCTransition:
    def __init__(self, ohlc_prev, ohlc):
        self.date_prev = ohlc_prev.date
        self.date = ohlc.date

        self.bullish_intra_day_swing = 0 if (ohlc_prev.c-ohlc.l) > (ohlc.h-ohlc_prev.c) else 1
        self.bullish_close = 0 if ohlc.c < ohlc_prev.c else 1

    def __eq__(self, other):
        return self.bullish_intra_day_swing == other.bullish_intra_day_swing and\
               self.bullish_close == other.bullish_close

ohlc_transitions = []
ohlc_prev = None

for line in raw_data:
    line_elts = line.decode("utf-8").split(",")

    ohlc = OHLC(datetime.datetime.strptime(line_elts[0], "%Y-%m-%d"),
                float(line_elts[1]),
                float(line_elts[2]),
                float(line_elts[3]),
                float(line_elts[4]))

    if ohlc_prev is not None:
        ohlc_transitions.append(OHLCTransition(ohlc_prev, ohlc))

    ohlc_prev = ohlc

for starting_idx in range(0,len(ohlc_transitions)-lookback+1):
    match = True
    for idx_offset in range(0, lookback):
        if ohlc_transitions[starting_idx+idx_offset] != ohlc_transitions[len(ohlc_transitions)-lookback+idx_offset]:
            match = False
            break
    if match:
        print("{0:%Y-%m-%d}".format(ohlc_transitions[starting_idx+lookback-1].date))
        if starting_idx+lookback < len(ohlc_transitions):
            print("{0} {1}".format(ohlc_transitions[starting_idx+lookback].bullish_intra_day_swing,
                                   ohlc_transitions[starting_idx+lookback].bullish_close))

