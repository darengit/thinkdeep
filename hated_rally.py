import yfinance as yf
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


def download_data(start_date: str = "1989-01-01"):
    spx = yf.download("^GSPC", start=start_date)
    vix = yf.download("^VIX", start=start_date)
    return spx, vix


def create_combined(spx: pd.DataFrame, vix: pd.DataFrame) -> pd.DataFrame:
    combined = pd.DataFrame(index=spx.index)
    combined["spx_high"] = spx["High"]
    combined["spx_low"] = spx["Low"]
    combined["spx_close"] = spx["Close"]

    # create spx_close_20dma
    combined["spx_close_20dma"] = combined["spx_close"].rolling(window=20).mean()
    # create spx_close_200dma
    combined["spx_close_200dma"] = combined["spx_close"].rolling(window=200).mean()


    vix_reindexed = vix.reindex(combined.index)
    combined["vix_high"] = vix_reindexed["High"]
    #create vix_high_20dma
    combined["vix_high_20dma"] = combined["vix_high"].rolling(window=20).mean()

    combined["vix_close"] = vix_reindexed["Close"]

    # fill vix_high with prev vix_close if missing
    combined["vix_close"] = combined["vix_close"].ffill()
    combined["vix_high"] = combined["vix_high"].fillna(combined["vix_close"])

    # Drop rows with missing SPX or vix data
    combined = combined.dropna(subset=["spx_high", "spx_low", "spx_close", "vix_high"])

    return combined

    
def raw_features(combined: pd.DataFrame) -> pd.DataFrame:
    # create column spx_close_20dma_slope, which is the slope of the 20dma over the past 5 days,
    # computed as a percentage change from 5 days ago to today divided by 5 to get a daily slope
    combined["spx_close_20dma_slope"] = (combined["spx_close_20dma"] - combined["spx_close_20dma"].shift(5)) / combined["spx_close_20dma"].shift(5) / 5

    # create column vix_high_20dma_slope, which is the slope of the vix high 20dma over the past 5 days,
    # computed as vix points/day
    combined["vix_high_20dma_slope"] = (combined["vix_high_20dma"] - combined["vix_high_20dma"].shift(5)) / 5

    # create column spx_pct_from_ath, which is the percentage difference between spx_close and the all time high of spx_close up to that day
    combined["spx_ath"] = combined["spx_close"].cummax() 
    combined["spx_pct_from_ath"] = (combined["spx_close"] - combined["spx_ath"]) / combined["spx_ath"]

    # create column spx_pct_from_250dh, which is the percentage difference between spx_close and the 250 day high of spx_close up to that day
    combined["spx_250dh"] = combined["spx_close"].rolling(window=250).max()
    combined["spx_pct_from_250dh"] = (combined["spx_close"] - combined["spx_250dh"]) / combined["spx_250dh"]

    # create column spx_1d_return, which is the percentage return of spx_close from today to tomorrow
    combined["spx_1d_return"] = (combined["spx_close"].shift(-1) - combined["spx_close"]) / combined["spx_close"]

    # create column spx_3d_return, which is the percentage return of spx_close from today to 3 days in the future
    combined["spx_3d_return"] = (combined["spx_close"].shift(-3) - combined["spx_close"]) / combined["spx_close"]

    # create column spx_10d_return, which is the percentage return of spx_close from today to 10 days in the future
    combined["spx_10d_return"] = (combined["spx_close"].shift(-10) - combined["spx_close"]) / combined["spx_close"]

    # create column spx_30d_return, which is the percentage return of spx_close from today to 30 days in the future
    combined["spx_30d_return"] = (combined["spx_close"].shift(-30) - combined["spx_close"]) / combined["spx_close"]

    #create column spx_90d_return, which is the percentage return of spx_close from today to 90 days in the future
    combined["spx_90d_return"] = (combined["spx_close"].shift(-90) - combined["spx_close"]) / combined["spx_close"]

    # create column spx_250d_return, which is the percentage return of spx_close from today to 250 days in the future
    combined["spx_250d_return"] = (combined["spx_close"].shift(-250) - combined["spx_close"]) / combined["spx_close"]


    # print tail of combined to check that new features are computed correctly
    print("Tail of combined DataFrame with new features:")
    print(combined.tail())

    # print combined between november of 2021 and january of 2022
    # make sure stdout prints everything without truncation
    pd.set_option("display.max_rows", None)
    print("Combined DataFrame between November 2021 and January 2022:")
    print(combined.loc["2021-11-01":"2022-01-31"])

    return combined

def main():
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 0)

    spx, vix = download_data()
    print("✅ Data downloaded.")
    combined = create_combined(spx, vix)
    print("✅ Combined DataFrame created.")
    combined = raw_features(combined)
    print("✅ Raw features computed.")

    # print all dates where spx is at an all time high (spx_pct_from_ath is 0),
    # and vix_high is over 19,
    # and spx_close_20dma_slope is greater than .003
    # and vix_high_20dma_slope is less than -0.3
    filtered = combined[
        (combined["spx_pct_from_ath"] == 0) &
        (combined["vix_high"] > 19) &
        (combined["spx_close_20dma_slope"] > .003) &
        (combined["vix_high_20dma_slope"] < -0.3)
    ]

    # print dates, vix_high, vix_high_20dma_slope, and spx_close_20dma_slope for filtered rows
    # also add spx_1d_return, spx_3d_return, spx_10d_return, spx_30d_return, spx_90d_return, and spx_250d_return
    print("Dates where conditions are met:")
    for date in filtered.index:
        print(f"{date.strftime('%Y-%m-%d')} | VIX: {filtered.loc[date, 'vix_high']:.2f} | VIX Slope: {filtered.loc[date, 'vix_high_20dma_slope']:.4f} | SPX Slope: {filtered.loc[date, 'spx_close_20dma_slope']:.4f} | 1D Ret: {filtered.loc[date, 'spx_1d_return']:.4f} | 3D Ret: {filtered.loc[date, 'spx_3d_return']:.4f} | 10D Ret: {filtered.loc[date, 'spx_10d_return']:.4f} | 30D Ret: {filtered.loc[date, 'spx_30d_return']:.4f} | 90D Ret: {filtered.loc[date, 'spx_90d_return']:.4f} | 250D Ret: {filtered.loc[date, 'spx_250d_return']:.4f}")

if __name__ == "__main__":
    main()
