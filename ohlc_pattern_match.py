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

#        self.open_transition = 0 if ohlc_after.o < ohlc_before.c else 1 #self.get_transition(ohlc_before, ohlc_after.o)
        self.high_transition = 0 if ohlc_after.h < ohlc_before.h else 1 #self.get_transition(ohlc_before, ohlc_after.h)
        self.low_transition = 0 if ohlc_after.l < ohlc_before.l else 1 #self.get_transition(ohlc_before, ohlc_after.l)
#        self.close_transition = 0 if ohlc_after.c < ohlc_before.c else 1 #self.get_transition(ohlc_before, ohlc_after.c)

#        self.open_close_transition = 0 if ohlc_after.c < ohlc_after.o else 1

    def __eq__(self, other):
        #return self.open_transition == other.open_transition and\
        return self.high_transition == other.high_transition and\
               self.low_transition == other.low_transition #and\
               #self.close_transition == other.close_transition and\
               #self.open_close_transition == other.open_close_transition
"""
    def get_transition(self, ohlc_before, new_value):
        transition = 0
        if new_value > ohlc_before.l:
            transition = 1
        if new_value > ohlc_before.c:
            transition = 2
        if new_value > ohlc_before.h:
            transition = 3

        return transition
"""
#dates = []
#opens = []
#highs = []
#lows = []
#closes = []

ohlc_transitions = []
ohlc_prev = None

for line in raw_data:
#dates = [datetime.datetime.strptime(line.decode("utf-8").split(",")[0], "%Y-%m-%d") for line in raw_data]
#print(dates)
#opens  = [float(line.decode("utf-8").split(",")[1]) for line in raw_data]
#highs  = [float(line.decode("utf-8").split(",")[2]) for line in raw_data]
#lows   = [float(line.decode("utf-8").split(",")[3]) for line in raw_data]
#closes = [float(line.decode("utf-8").split(",")[4]) for line in raw_data]
#print(highs)
    line_elts = line.decode("utf-8").split(",")
    #dates.append(datetime.datetime.strptime(line_elts[0], "%Y-%m-%d"))
    #opens.append(float(line_elts[1]))
    #highs.append(float(line_elts[2]))
    #lows.append(float(line_elts[3]))
    #closes.append(float(line_elts[4]))

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


"""
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

        self.open_transition = self.get_transition(ohlc_before, ohlc_after.o)
        self.high_transition = self.get_transition(ohlc_before, ohlc_after.h)
        self.low_transition = self.get_transition(ohlc_before, ohlc_after.l)
        self.close_transition = self.get_transition(ohlc_before, ohlc_after.c)

        self.open_close_transition = 0 if ohlc_after.c < ohlc_after.o else 1

    def __eq__(self, other):
        return self.open_transition == other.open_transition and\
               self.high_transition == other.high_transition and\
               self.low_transition == other.low_transition and\
               self.close_transition == other.close_transition and\
               self.open_close_transition == other.open_close_transition

    def get_transition(self, ohlc_before, new_value):
        transition = 0
        if new_value > ohlc_before.l:
            transition = 1
        if new_value > ohlc_before.c:
            transition = 2
        if new_value > ohlc_before.h:
            transition = 3

        return transition
"""
    

"""
result_count = int(sys.argv[2])
forward_days = int(sys.argv[3])

highs_to_compare = highs[0:lookback-1]
lows_to_compare  = lows[0:lookback-1]


class ComparableValue:
    def __init__(self, idx, value):
        self.idx = idx
        self.comparable = value

historical_comparisons = []
for i in range(0,len(dates)-lookback-1):
    highs_compare_to = highs[i:i+lookback-1]
    highs_corrcoef = numpy.corrcoef(highs_to_compare, highs_compare_to)[0][1]

    lows_compare_to = lows[i:i+lookback-1]
    lows_corrcoef = numpy.corrcoef(lows_to_compare, lows_compare_to)[0][1]

    curr_comparable = ComparableValue(i, highs_corrcoef+lows_corrcoef)
    historical_comparisons.append(curr_comparable)

historical_comparisons.sort(key=lambda x:x.comparable, reverse=True)

for comparable in historical_comparisons[0:result_count]:
    print("{0:%Y-%m-%d} {1:.3f}".format(dates[comparable.idx], comparable.comparable))
    for i in range(1,forward_days):
        if comparable.idx-i >= 0:
            print("{0:.2f} {1:.2f}".format((highs[comparable.idx-i]-highs[comparable.idx])/highs[comparable.idx]*100,
                                           (lows[comparable.idx-i]-lows[comparable.idx])/lows[comparable.idx]*100))
"""
