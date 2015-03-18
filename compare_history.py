import sys
import numpy

from utils.db import local_pymysql_conn, load_all_ohlc

tablename = sys.argv[1]
lookback = int(sys.argv[2])
result_count = int(sys.argv[3])
forward_days = int(sys.argv[4])

conn = local_pymysql_conn()
(dates, opens, highs, lows, closes) = load_all_ohlc(conn, tablename)
dates.reverse()
opens.reverse()
highs.reverse()
lows.reverse()
closes.reverse()

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

