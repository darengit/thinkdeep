
import urllib.request
import datetime
import sys
import os

import numpy
import matplotlib.pyplot
import matplotlib.dates

today = datetime.date.today()

url = "http://ichart.finance.yahoo.com/table.csv?s=%5EGSPC&d=" + str(today.month - 1) + "&e=" + str(today.day) + "&f=" + str(today.year) + "&g=d&a=0&b=3&c=1950&ignore=.csv"
response = urllib.request.urlopen(url)

raw_data = list(response)
#print(raw_data)
raw_data.pop(0)
raw_data.reverse()

dates = [datetime.datetime.strptime(line.decode("utf-8").split(",")[0], "%Y-%m-%d") for line in raw_data]
#print(dates)
opens  = [float(line.decode("utf-8").split(",")[1]) for line in raw_data]
highs  = [float(line.decode("utf-8").split(",")[2]) for line in raw_data]
lows   = [float(line.decode("utf-8").split(",")[3]) for line in raw_data]
closes = [float(line.decode("utf-8").split(",")[4]) for line in raw_data]
#print(highs)

start_date = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d")
end_date = datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d")

start_date_idx = dates.index(start_date)
end_date_idx = dates.index(end_date)

matplotlib.pyplot.plot_date(x=dates[start_date_idx:end_date_idx], y=highs[start_date_idx:end_date_idx], fmt="-")
matplotlib.pyplot.plot_date(x=dates[start_date_idx:end_date_idx], y=lows[start_date_idx:end_date_idx], fmt="-")
matplotlib.pyplot.grid(True)
matplotlib.pyplot.show()
