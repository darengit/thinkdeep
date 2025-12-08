# main.py
from util.get_tickers import get_superset_of_tickers
from util.yfinance_helper import get_ticker_data_with_cache

# Get the full ticker list
tickers = get_superset_of_tickers()

# Fetch sector, industry, previous year last close, and latest close
df = get_ticker_data_with_cache(tickers)

# Print only the first 5 rows to avoid huge output
print(df.head())


df["Pct Change"] = (
    (df["Latest Close"] - df["Prev Year Last Close"]) 
    / df["Prev Year Last Close"]
)


df.to_csv("output.csv", index=False)

