import yfinance as yf
import pandas as pd

# Download VIX data
vix = yf.download("^VIX", start="1990-01-01")
vix.columns = vix.columns.get_level_values(0)
print(vix.columns)

# add a column to vix for the day of the week, where Monday is 0 and Friday is 4
vix["day_of_week"] = vix.index.dayofweek

print(vix.tail())

# print columns of vix
print(vix.columns)

# for each day of the week, compute statistics on vix high and vix close
stats = vix.groupby("day_of_week").agg({
    "High": ["mean", "median", "std"],
    "Close": ["mean", "median", "std"]
})

print(stats)