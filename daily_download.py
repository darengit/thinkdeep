import math

from utils.config import *
from utils.db import local_pymysql_conn, yahoo_finance_download

conn = local_pymysql_conn()

for tablename in TABLE_TICKER_MAPPING.keys():
    yahoo_finance_download(conn, tablename)
    print("...downloaded {} into db".format(tablename))

def calc_std(base, base_plus_delta, std):
    return round(100*(base_plus_delta-base)/base/std, 2)

def daily_std_moves(conn):
    cursor = conn.cursor()

    cursor.execute("select s.date, s.high, s.low, v.high from sp500 s inner join vix v on s.date=v.date order by s.date")

    first_values = cursor.fetchone()
    prev_high = first_values[1]
    prev_low = first_values[2]
    prev_vol = first_values[3]

    write_cursor = conn.cursor()
    write_cursor.execute("truncate daily_std_moves")
    write_cursor.execute("insert into daily_std_moves (date,low_to_high) values ('{0}',{1})".\
        format(first_values[0],calc_std(prev_low,prev_high,prev_vol/math.sqrt(252))))

    for row in cursor:
        two_day_vol = max(prev_vol, row[3]) / math.sqrt(252/2)
        write_cursor.execute("insert into daily_std_moves values('{0}',{1},{2},{3})"\
            .format(row[0],
                    calc_std(row[2], row[1], row[3]/math.sqrt(252)),
                    calc_std(prev_low, row[1], two_day_vol),
                    calc_std(prev_high, row[2], two_day_vol)))
        prev_high = row[1]
        prev_low = row[2]
        prev_vol = row[3]

    conn.commit()

daily_std_moves(conn)
print("...computed std of daily and overnight moves")

conn.close()
