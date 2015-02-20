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
raw_data.pop(0)
raw_data.reverse()
if len(sys.argv) >= 3:
    raw_data.append(sys.argv[3].encode("utf-8"))

class OHLC:
    def __init__(self, date, o, h, l, c):
        self.date = date
        self.o = o
        self.h = h
        self.l = l
        self.c = c


class OHLCTransition:
    def __init__(self, ohlc_before, ohlc_after):
        self.date_before = ohlc_before.date
        self.date_after = ohlc_after.date

        self.high_transition = 0 if ohlc_after.h < ohlc_before.h else 1
        self.low_transition = 0 if ohlc_after.l < ohlc_before.l else 1

    def __eq__(self, other):
        return self.high_transition == other.high_transition and\
               self.low_transition == other.low_transition

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
        print("{0:%Y-%m-%d}".format(ohlc_transitions[starting_idx+lookback-1].date_after))
        if starting_idx+lookback < len(ohlc_transitions):
            print(ohlc_transitions[starting_idx+lookback].high_transition)
            print(ohlc_transitions[starting_idx+lookback].low_transition)

