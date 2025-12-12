'''

i have the following data in output.csv

Ticker,Sector,Industry,Prev Year Last Close,Latest Close,Pct Change
A,Healthcare,Diagnostics & Research,133.50538635253906,141.97999572753906,0.06347765889101767
AA,Basic Materials,Aluminum,37.302852630615234,43.22999954223633,0.15889259114614093
AAL,Industrials,Airlines,17.43000030517578,15.029999732971191,-0.13769366208742506
AAON,Industrials,Building Products & Equipment,117.14509582519533,82.08999633789062,-0.2992451304970901
AAPL,Technology,Consumer Electronics,249.2925262451172,277.6199951171875,0.113631440535916
ABBV,Healthcare,Drug Manufacturers - General,171.69651794433594,221.13499450683594,0.2879410552666419
ABNB,Consumer Cyclical,Travel Services,131.41000366210938,125.04499816894531,-0.048436232522527066
ABT,Healthcare,Medical Devices,111.00659942626952,121.81999969482422,0.09741222886245562
ACGL,Financial Services,Insurance - Diversified,92.3499984741211,92.75499725341797,0.004385476837992221


what i want to do is to load this data into a dataframe, then sort by pct change
then load data for each sector into a dataframe, and sort each by pct change
then i would like to construct a basket of 100 names, 50 pairs, and construct it in the following manner:

take the biggest outperformer from the overall list that's not already in my basket
take the biggest underperformer from the same sector that's not already in my basket
put both into my basket

then

take the biggest underperformer from the overall list that's not already in my basket
then take the biggest outperformer from the same sector that's not already in my basket
put both into my basket

i want to repeat the above until i have 'size', an input, names in my basket
then return a df with the basket as a dataframe


'''

import pandas as pd

def build_basket(csv_path, size=100):
    # -------------------------------------------------------------
    # 1. Load CSV
    # -------------------------------------------------------------
    df = pd.read_csv(csv_path)

    # Ensure pct change is numeric
    df["Pct Change"] = pd.to_numeric(df["Pct Change"], errors="coerce")

    # -------------------------------------------------------------
    # 2. Sort overall by pct change
    # -------------------------------------------------------------
    df_sorted_all = df.sort_values("Pct Change", ascending=False).reset_index(drop=True)

    # Split outperformers and underperformers
    outperformers = df_sorted_all.copy()
    underperformers = df_sorted_all.sort_values("Pct Change", ascending=True).reset_index(drop=True)

    # -------------------------------------------------------------
    # 3. Create sorted lists for each sector
    # -------------------------------------------------------------
    sector_groups = {}
    for sector in df["Sector"].unique():
        dsec = df[df["Sector"] == sector].sort_values("Pct Change", ascending=False).reset_index(drop=True)
        sector_groups[sector] = dsec

    # Also sector-level underperformers
    sector_groups_under = {}
    for sector in df["Sector"].unique():
        dsec = df[df["Sector"] == sector].sort_values("Pct Change", ascending=True).reset_index(drop=True)
        sector_groups_under[sector] = dsec

    # -------------------------------------------------------------
    # 4. Basket logic
    # -------------------------------------------------------------
    basket = []
    used = set()     # keep track of tickers added
    idx_out = 0      # pointer for global outperformers
    idx_under = 0    # pointer for global underperformers

    # pointers for sector-level lists
    sector_ptr_out = {sector: 0 for sector in df["Sector"].unique()}
    sector_ptr_under = {sector: 0 for sector in df["Sector"].unique()}

    # Helper functions to get next unused ticker
    def next_unused_from_list(dframe, start_idx=0):
        for i in range(start_idx, len(dframe)):
            t = dframe.loc[i, "Ticker"]
            if t not in used:
                return i, t
        return None, None

    # -------------------------------------------------------------
    # 5. Build basket until reaching desired size
    # -------------------------------------------------------------
    while len(basket) < size:

        # -----------------------------
        # Step A:
        # biggest overall outperformer → biggest sector underperformer
        # -----------------------------
        idx_out, top_out = next_unused_from_list(outperformers, idx_out)
        if top_out is None:
            break

        sector = df.loc[df["Ticker"] == top_out, "Sector"].values[0]

        # find biggest *underperformer* in same sector
        s_under = sector_groups_under[sector]
        sptr = sector_ptr_under[sector]
        sptr, sec_under = next_unused_from_list(s_under, sptr)
        if sec_under is None:
            break

        # add pair
        basket.append(top_out)
        used.add(top_out)
        basket.append(sec_under)
        used.add(sec_under)

        # update sector pointer
        sector_ptr_under[sector] = sptr + 1

        # Stop if full
        if len(basket) >= size:
            break

        idx_out += 1

        # -----------------------------
        # Step B:
        # biggest overall underperformer → biggest sector outperformer
        # -----------------------------
        idx_under, top_under = next_unused_from_list(underperformers, idx_under)
        if top_under is None:
            break

        sector = df.loc[df["Ticker"] == top_under, "Sector"].values[0]

        s_out = sector_groups[sector]
        sptr = sector_ptr_out[sector]
        sptr, sec_out = next_unused_from_list(s_out, sptr)
        if sec_out is None:
            break

        # add pair
        basket.append(top_under)
        used.add(top_under)
        basket.append(sec_out)
        used.add(sec_out)

        # update pointer
        sector_ptr_out[sector] = sptr + 1
        idx_under += 1

    # -------------------------------------------------------------
    # 6. Return final basket dataframe
    # -------------------------------------------------------------
    basket_df = df[df["Ticker"].isin(basket)].copy()
    # Optional: reorder by pct change
    basket_df = basket_df.sort_values("Pct Change", ascending=False).reset_index(drop=True)

    return basket_df




basket_df = build_basket("output.csv", size=100)
print(basket_df)


basket_df.to_csv("basket_output.csv", index=False)
