import sys
import math

#import matplotlib.pyplot

from utils.db import local_pymysql_conn, load_ohlc

start_date = sys.argv[1]
end_date = sys.argv[2]
direction = sys.argv[3]

conn = local_pymysql_conn()

(dates, o, highs, lows, c) = load_ohlc(conn, "sp500", start_date, end_date)
(vix_dates, o, vix_highs, l, c) = load_ohlc(conn, "vix", start_date, end_date)
vix = dict(zip(vix_dates, vix_highs))

def analyze_std_move(dates, values, vix):
    max_vol = vix[dates[0]]
    for i in range(1,len(dates)):
        max_vol = max(max_vol, vix[dates[i]])
        std = max_vol * (i+1) / math.sqrt(252)
        print("{0} {1}".format(dates[i], 100*(values[i]-values[0])/values[0]/std))
        

if direction == "down":
    analyze_std_move(dates, [highs[0]]+lows[1:], vix)
else:
    analyze_std_move(dates, [lows[0]]+highs[1:], vix)
