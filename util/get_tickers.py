import pandas as pd
import urllib.request

def read_html_with_user_agent(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
    )
    with urllib.request.urlopen(req) as response:
        html = response.read()
    return pd.read_html(html)


def extract_ticker_column(df):
    """Return the column containing tickers (Symbol/Ticker/etc)."""
    possible_cols = ["Symbol", "Ticker", "Ticker symbol", "Code", "Symbol.1"]

    for col in df.columns:
        if col in possible_cols:
            return df[col]

    # fallback: guess by pattern (all caps, short strings)
    for col in df.columns:
        if df[col].dtype == object:
            if df[col].str.match(r"^[A-Z.\-]{1,6}$", na=False).mean() > 0.5:
                return df[col]

    raise ValueError("Could not find ticker column in table.")


def get_sp_index(url, name):
    print(f"-> Fetching {name} components...")

    tables = read_html_with_user_agent(url)

    # find a table that likely contains constituents
    for df in tables:
        try:
            tickers_raw = extract_ticker_column(df)
            tickers = set(tickers_raw.str.replace('.', '-', regex=False).dropna().tolist())
            print(f"   Retrieved {len(tickers)} tickers from {name}")
            return tickers
        except Exception:
            continue

    raise RuntimeError(f"Failed to find ticker column for {name}")


def get_superset_of_tickers():
    sp500 = get_sp_index(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        "S&P 500"
    )

    sp400 = get_sp_index(
        "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies",
        "S&P 400"
    )

    superset = sorted(sp500 | sp400)

    print("-" * 40)
    print(f"✅ Total unique tickers in superset: {len(superset)}")
    print("-" * 40)

    return superset


if __name__ == "__main__":
    tickers = get_superset_of_tickers()
    print("First 20 tickers:")
    print(tickers[:20])

