import urllib.request
import sys
import re
import time

ticker = sys.argv[1]

url = "http://finance.yahoo.com/q?s=" + ticker


while True:
    print((re.search('<span id="yfs_l10_' + ticker.replace("^", "\^") + '">([0-9,\.]*)</span>', list(urllib.request.urlopen(url))[180].decode("utf-8"))).group(1))
    time.sleep(2)

