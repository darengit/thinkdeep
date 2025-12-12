'''


I have 3 csv files IJH_holdings.csv IVV_holdings.csv and IWB_holdings.csv. They each have this format:


iShares Core S&P Mid-Cap ETF
Fund Holdings as of,"Dec 11, 2025"
Inception Date,"May 22, 2000"
Shares Outstanding,"1,536,000,000.00"
Stock,"-"
Bond,"-"
Cash,"-"
Other,"-"
 
Ticker,Name,Type,Sector,Asset Class,Market Value,Notional Value,Quantity,Price,Location,Exchange,Currency,FX Rate,Market Currency,Accrual Date,Notional Weight,Market Weight
"FIX","COMFORT SYSTEMS USA INC","EQUITY","Industrials","Equity","1,156,178,429.64","1,156,178,429.64","1,128,067.00","1,024.92","United States","New York Stock Exchange Inc.","USD","1.00","USD","-","1.10","1.10"
"CIEN","CIENA CORP","EQUITY","Information Technology","Equity","1,098,050,498.64","1,098,050,498.64","4,530,472.00","242.37","United States","New York Stock Exchange Inc.","USD","1.00","USD","-","1.05","1.05"
"COHR","COHERENT CORP","EQUITY","Information Technology","Equity","988,891,071.50","988,891,071.50","4,981,819.00","198.50","United States","New York Stock Exchange Inc.","USD","1.00","USD","-","0.94","0.94"
"FLEX","FLEX LTD","EQUITY","Information Technology","Equity","854,203,646.43","854,203,646.43","12,029,343.00","71.01","United States","NASDAQ","USD","1.00","USD","-","0.81","0.82"
"LITE","LUMENTUM HOLDINGS INC","EQUITY","Information Technology","Equity","832,433,794.56","832,433,794.56","2,237,184.00","372.09","United States","NASDAQ","USD","1.00","USD","-","0.79","0.80"
"PSTG","PURE STORAGE INC CLASS A","EQUITY","Information Technology","Equity","754,969,016.88","754,969,016.88","9,950,824.00","75.87","United States","New York Stock Exchange Inc.","USD","1.00","USD","-","0.72","0.72"
"UTHR","UNITED THERAPEUTICS CORP","EQUITY","Health Care","Equity","707,844,639.37","707,844,639.37","1,448,987.00","488.51","United States","NASDAQ","USD","1.00","USD","-","0.68","0.68"


I would like to skip the headers and start grabbing the Ticker from each row in the files, then union all tickers found

'''


import pandas as pd

def extract_tickers(csv_file):
    """
    Reads a CSV file and returns a list of tickers,
    automatically skipping metadata rows before the header line.
    """
    # Find the header row (the line that starts with "Ticker")
    with open(csv_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if line.strip().startswith("Ticker"):
                header_row = i
                break
        else:
            raise ValueError(f"No header line found in {csv_file}")

    # Read CSV starting from the header row
    df = pd.read_csv(csv_file, skiprows=header_row)

    # Extract tickers as a list, stripping whitespace/quotes
    tickers = df["Ticker"].astype(str).str.strip().tolist()
    return tickers

def all_tickers(csv_files):
    """
    Takes a list of CSV file paths and returns a sorted list
    of all unique tickers found across the files.
    """
    ticker_set = set()  # ensure uniqueness
    for f in csv_files:
        ticker_set.update(extract_tickers(f))
    return sorted(ticker_set)  # return a sorted list

