from utils.config import *
from utils.db import local_pymysql_conn, yahoo_finance_download

conn = local_pymysql_conn()
for tablename in TABLE_TICKER_MAPPING.keys():
    yahoo_finance_download(conn, tablename)
    print("downloaded {} into db".format(tablename))


"""
import urllib.request
import datetime
import os
import pymysql


def yahoo_finance_download(conn, tablename):
    today = datetime.date.today()
    url = "http://ichart.finance.yahoo.com/table.csv?s=%5E{0}&d={1}&e={2}&f={3}&g=d&a=0&b=3&c=1950&ignore=.csv".format(TABLE_TICKER_MAPPING[tablename], str(today.month - 1), str(today.day), str(today.year))
    response = urllib.request.urlopen(url)
    response.readline() # header line

    cur.execute("truncate {}".format(tablename))
    for line in response:
        elts = line.decode("utf-8").split(",")
        cur.execute("insert into {0} values ('{1}',{2},{3},{4},{5})".format(tablename, *elts))
    conn.commit()


TABLE_TICKER_MAPPING = {"sp500":"GSPC",
                        "vix":"VIX"}

conn = pymysql.connect(host="localhost", user="root", passwd="", database="db")
conn.autocommit(False)
cur = conn.cursor()

for tablename in TABLE_TICKER_MAPPING.keys():
    yahoo_finance_download(conn, tablename)
    print("downloaded {} into db".format(tablename))

conn.close()
"""


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
