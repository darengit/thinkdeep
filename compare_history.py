import urllib.request
import datetime
import os
import numpy

today = datetime.date.today()

url = "http://ichart.finance.yahoo.com/table.csv?s=%5EGSPC&d=" + str(today.month - 1) + "&e=" + str(today.day) + "&f=" + str(today.year) + "&g=d&a=0&b=3&c=1950&ignore=.csv"
response = urllib.request.urlopen(url)

raw_data = list(response)
#print(raw_data)
raw_data.pop(0)

dates = [datetime.datetime.strptime(line.decode("utf-8").split(",")[0], "%Y-%m-%d") for line in raw_data]
#print(dates)
opens  = [float(line.decode("utf-8").split(",")[1]) for line in raw_data]
highs  = [float(line.decode("utf-8").split(",")[2]) for line in raw_data]
lows   = [float(line.decode("utf-8").split(",")[3]) for line in raw_data]
closes = [float(line.decode("utf-8").split(",")[4]) for line in raw_data]
#print(highs)


lookback = 130

highs_to_compare = highs[0:lookback-1]
lows_to_compare  = lows[0:lookback-1]


class ComparableValue:
    def __init__(self, idx, value):
        self.idx = idx
        self.comparable = value

historical_comparisons = []
for i in range(0,len(dates)-lookback-1):
#    if i%100 == 0:
#        print("running the {}th element".format(i))
    highs_compare_to = highs[i:i+lookback-1]
    highs_corrcoef = numpy.corrcoef(highs_to_compare, highs_compare_to)[0][1]

    lows_compare_to = lows[i:i+lookback-1]
    lows_corrcoef = numpy.corrcoef(lows_to_compare, lows_compare_to)[0][1]

    curr_comparable = ComparableValue(i, highs_corrcoef+lows_corrcoef)
#    print("{0} {1}".format(i, highs_corrcoef+lows_corrcoef))
    historical_comparisons.append(curr_comparable)

historical_comparisons.sort(key=lambda x:x.comparable, reverse=True)

for comparable in historical_comparisons[0:40]:
    print("{0} {1}".format(dates[comparable.idx], comparable.comparable))

"""
dir = "/Users/dzou/R/data/"
file = "sp.csv"

os.system("mkdir -p " + dir);
fh = open(dir + file, "w+");
fh.write(response.read().decode("utf-8"))
fh.close

print("successfully downloaded : " + url + " and saved it to : " + dir + file)

url = "http://ichart.finance.yahoo.com/table.csv?s=%5EVIX&d=" + str(today.month - 1) + "&e=" + str(today.day) + "&f=" + str(today.year) + "&g=d&a=0&b=2&c=1990&ignore=.csv"

response = urllib.request.urlopen(url)

dir = "/Users/dzou/R/data/"
file = "vix.csv"

os.system("mkdir -p " + dir);
fh = open(dir + file, "w+");
fh.write(response.read().decode("utf-8"))
fh.close

print("successfully downloaded : " + url + " and saved it to : " + dir + file)
"""
