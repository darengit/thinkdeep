import sys

#import matplotlib.pyplot

from utils.db import local_pymysql_conn, load_ohlc
from utils.graph import graph_ohlc_voladj

tablename = sys.argv[1]
vol_tablename = sys.argv[2]
start_date = sys.argv[3]
end_date = sys.argv[4]

conn = local_pymysql_conn()

(dates, opens, highs, lows, closes) = load_ohlc(conn, tablename, start_date, end_date)
(vdates, vopens, vhighs, vlows, vcloses) = load_ohlc(conn, vol_tablename, start_date, end_date)
#(high_pivots, low_pivots) = upside_down_pivots(dates, highs, lows)

#graph_ohlc_pivots(dates, opens, highs, lows, closes, high_pivots, low_pivots)
graph_ohlc_voladj(dates, opens, highs, lows, closes, vcloses)
