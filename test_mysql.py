import pymysql

conn = pymysql.connect(host="localhost", user="root", passwd="", database="db")
conn.autocommit(False)
cur = conn.cursor()

cur.execute("insert into sp500 values ('2015-03-05',12,12,12,12)")
conn.commit()
conn.close()

