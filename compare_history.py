import urllib.request
import datetime
import os
import sys
import numpy

today = datetime.date.today()

url = "http://ichart.finance.yahoo.com/table.csv?s=%5EGSPC&d=" + str(today.month - 1) + "&e=" + str(today.day) + "&f=" + str(today.year) + "&g=d&a=0&b=3&c=1950&ignore=.csv"
response = urllib.request.urlopen(url)

raw_data = list(response)
#print(raw_data)
raw_data.pop(0)

dates = []
opens = []
highs = []
lows = []
closes = []

for line in raw_data:
#dates = [datetime.datetime.strptime(line.decode("utf-8").split(",")[0], "%Y-%m-%d") for line in raw_data]
#print(dates)
#opens  = [float(line.decode("utf-8").split(",")[1]) for line in raw_data]
#highs  = [float(line.decode("utf-8").split(",")[2]) for line in raw_data]
#lows   = [float(line.decode("utf-8").split(",")[3]) for line in raw_data]
#closes = [float(line.decode("utf-8").split(",")[4]) for line in raw_data]
#print(highs)
    line_elts = line.decode("utf-8").split(",")
    dates.append(datetime.datetime.strptime(line_elts[0], "%Y-%m-%d"))
    opens.append(float(line_elts[1]))
    highs.append(float(line_elts[2]))
    lows.append(float(line_elts[3]))
    closes.append(float(line_elts[4]))


lookback = int(sys.argv[1])
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

