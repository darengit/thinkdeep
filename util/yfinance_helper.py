import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List
import os

CACHE_FILE = "cache.csv"

def get_ticker_data_with_cache(tickers: List[str], batch_size: int = 50) -> pd.DataFrame:
    """
    Fetch sector, industry, previous year last close (cached) and latest close (fresh)
    for a list of tickers. Updates cache.csv for future runs.

    Args:
        tickers: list of ticker symbols
        batch_size: number of tickers to process per batch for latest closes (default 50)

    Returns:
        pd.DataFrame with columns:
        Ticker, Sector, Industry, Prev Year Last Close, Latest Close
    """
    today = datetime.now()
    current_year = today.year
    prev_year_start = datetime(current_year - 1, 12, 26)
    prev_year_end   = datetime(current_year, 1, 1)  # exclusive
    latest_start = today - timedelta(days=5)
    latest_end   = today

    # Load cache if exists
    if os.path.exists(CACHE_FILE):
        cache_df = pd.read_csv(CACHE_FILE, index_col=0)
    else:
        cache_df = pd.DataFrame(columns=["Ticker", "Sector", "Industry", "Prev Year Last Close"])
        cache_df.set_index("Ticker", inplace=True)

    results = []

    total_tickers = len(tickers)
    for i in range(0, total_tickers, batch_size):
        batch = tickers[i:i+batch_size]

        # --- Latest close batch download ---
        try:
            hist = yf.download(batch, start=latest_start, end=latest_end, group_by="ticker", progress=False)
        except Exception as e:
            print(f"Error downloading latest prices for batch {batch}: {e}")
            continue

        for t in batch:
            # --- Latest Close ---
            latest_close = None
            try:
                # Handle single vs multiple ticker DataFrame structure
                if len(batch) == 1:
                    ticker_hist = hist
                else:
                    ticker_hist = hist[t]

                latest_close = ticker_hist["Close"].iloc[-1]
            except Exception:
                print(f"Could not fetch latest price for {t}")
                continue

            # --- Check cache for sector/industry and prev year last close ---
            if t in cache_df.index and pd.notna(cache_df.loc[t, "Sector"]) \
               and pd.notna(cache_df.loc[t, "Industry"]) \
               and pd.notna(cache_df.loc[t, "Prev Year Last Close"]):
                sector = cache_df.loc[t, "Sector"]
                industry = cache_df.loc[t, "Industry"]
                prev_year_last_close = cache_df.loc[t, "Prev Year Last Close"]
            else:
                # Fetch from yfinance
                ticker_obj = yf.Ticker(t)
                info = ticker_obj.info
                sector = info.get("sector")
                industry = info.get("industry")

                # Previous year last close
                hist_prev = ticker_obj.history(start=prev_year_start, end=prev_year_end)
                if hist_prev.empty:
                    prev_year_last_close = None
                else:
                    prev_year_last_close = hist_prev["Close"].iloc[-1]

                # Update cache
                cache_df.loc[t] = {
                    "Sector": sector,
                    "Industry": industry,
                    "Prev Year Last Close": prev_year_last_close
                }

            results.append({
                "Ticker": t,
                "Sector": sector,
                "Industry": industry,
                "Prev Year Last Close": prev_year_last_close,
                "Latest Close": latest_close
            })

        print(f"Processed tickers {i+1} to {i+len(batch)} of {total_tickers}")
        #sleepSec = 60
        #print(f"sleeping {sleepSec} seconds")

    # Save updated cache
    cache_df.to_csv(CACHE_FILE)

    df = pd.DataFrame(results)
    return df

