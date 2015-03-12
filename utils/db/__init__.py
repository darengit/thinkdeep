import urllib.request
import datetime
import pymysql
from utils.config import *

def pymysql_conn(credentials):
    return pymysql.connect(**credentials)

def local_pymysql_conn():
    return pymysql_conn(MYSQL_CREDENTIALS)

def yahoo_finance_download(conn, tablename):
    today = datetime.date.today()
    url = "http://ichart.finance.yahoo.com/table.csv?s=%5E{0}&d={1}&e={2}&f={3}&g=d&a=0&b=3&c=1950&ignore=.csv".format(TABLE_TICKER_MAPPING[tablename], str(today.month - 1), str(today.day), str(today.year))
    response = urllib.request.urlopen(url)
    response.readline() # header line

    conn.cursor().execute("truncate {}".format(tablename))
    for line in response:
        elts = line.decode("utf-8").split(",")
        conn.cursor().execute("insert into {0} values ('{1}',{2},{3},{4},{5})".format(tablename, *elts))
    conn.commit()

def load_ohlc(conn, tablename, start_date, end_date):
    cursor = conn.cursor()
    cursor.execute("select date,open,high,low,close from {0} where date between '{1}' and '{2}' order by date".format(tablename, start_date, end_date))

    dates = []
    opens = []
    highs = []
    lows = []
    closes = []

    for row in cursor:
        dates.append(row[0])
        opens.append(float(row[1]))
        highs.append(float(row[2]))
        lows.append(float(row[3]))
        closes.append(float(row[4]))

    return (dates, opens, highs, lows, closes)
