import urllib.request
import re
import time

url = "https://www.google.com/finance?q=INDEXSP%3A.INX"

while True:
    try:
        print((re.search('<span id="ref_626307_l">([0-9,\.]*)</span>', list(urllib.request.urlopen(url))[179].decode("utf-8"))).group(1))
    except:
        continue
    finally:
        time.sleep(2)
