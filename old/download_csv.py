import urllib.request
import datetime
import os

today = datetime.date.today()

url = "http://ichart.finance.yahoo.com/table.csv?s=%5EGSPC&d=" + str(today.month - 1) + "&e=" + str(today.day) + "&f=" + str(today.year) + "&g=d&a=0&b=3&c=1950&ignore=.csv"
response = urllib.request.urlopen(url)

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
