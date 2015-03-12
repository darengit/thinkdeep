import sys

#import matplotlib.pyplot

from utils.db import local_pymysql_conn, load_ohlc
from utils.graph import graph_ohlc_pivots, alternating_pivots, fuzzy_pivots

tablename = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]

conn = local_pymysql_conn()

(dates, opens, highs, lows, closes) = load_ohlc(conn, tablename, start_date, end_date)
(high_pivots, low_pivots) = alternating_pivots(dates, highs, lows)

graph_ohlc_pivots(dates, opens, highs, lows, closes, high_pivots, low_pivots)

