import yfinance as yf
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression


def download_data(start_date: str = "2010-01-01"):
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
    combined["vix_close"] = vix_reindexed["Close"]

    # fill vix_high with prev vix_close if missing
    combined["vix_close"] = combined["vix_close"].ffill()
    combined["vix_high"] = combined["vix_high"].fillna(combined["vix_close"])
    #combined = combined.drop(columns=["vix_close"])

    # Drop rows with missing SPX or vix data
    combined = combined.dropna(subset=["spx_high", "spx_low", "spx_close", "vix_high"])

    return combined

    
# as well as spx_prev_close_to_high_pct, spx_prev_close_to_low_pct
# as well as spx_prev_high_to_close_pct, spx_prev_low_to_close_pct
# as well as spx_prev_prev_close_to_prev_high_pct,
# spx_prev_prev_close_to_prev_low_pct
# as well as spx_prev_prev_high_to_close_pct, spx_prev_prev_low_to_close_pct
# as well as spx_close_20dma_ratio, spx_prev_close_20dma_ratio
# as well as spx_prev_prev_close_20dma_ratio
# as well as spx_close_200dma_ratio, spx_prev_close_200dma_ratio
# as well as spx_prev_prev_close_200dma_ratio
def raw_features(combined: pd.DataFrame) -> pd.DataFrame:
    # create column spx_high_to_close_ratio, which is the ratio
    # of current day's spx_high to current day's spx_close
    combined["spx_high_to_close_ratio"] = combined["spx_high"] / combined["spx_close"]

    # create column spx_low_to_close_ratio, which is the ratio
    # of current day's spx_low to current day's spx_close
    combined["spx_low_to_close_ratio"] = combined["spx_low"] / combined["spx_close"]

    # create column spx_prev_close_to_high_ratio, which is the ratio
    # of previous day's spx_close to current day's spx_high
    combined["spx_prev_close_to_high_ratio"] = combined["spx_close"].shift(1) / combined["spx_high"]

    # create column spx_prev_close_to_low_ratio, which is the ratio
    # of previous day's spx_close to current day's spx_low
    combined["spx_prev_close_to_low_ratio"] = combined["spx_close"].shift(1) / combined["spx_low"]

    # create column spx_prev_high_to_close_ratio, which is the ratio
    # of previous day's spx_high to previous day's spx_close
    combined["spx_prev_high_to_close_ratio"] = combined["spx_high"].shift(1) / combined["spx_close"].shift(1)

    # create column spx_prev_low_to_close_ratio, which is the ratio
    # of previous day's spx_low to previous day's spx_close
    combined["spx_prev_low_to_close_ratio"] = combined["spx_low"].shift(1) / combined["spx_close"].shift(1)

    # create column spx_prev2_close_to_prev_high_ratio, which is the ratio
    # of previous-previous day's spx_close to previous day's spx_high
    combined["spx_prev2_close_to_prev_high_ratio"] = combined["spx_close"].shift(2) / combined["spx_high"].shift(1)

    # create column spx_prev2_close_to_prev_low_ratio, which is the ratio
    # of previous-previous day's spx_close to previous day's spx_low
    combined["spx_prev2_close_to_prev_low_ratio"] = combined["spx_close"].shift(2) / combined["spx_low"].shift(1)

    # create column spx_prev2_high_to_close_ratio, which is the ratio
    # of previous-previous day's spx_high to previous-previous day's spx_close
    combined["spx_prev2_high_to_close_ratio"] = combined["spx_high"].shift(2) / combined["spx_close"].shift(2)

    # create column spx_prev2_low_to_close_ratio, which is the ratio
    # of previous-previous day's spx_low to previous-previous day's spx_close
    combined["spx_prev2_low_to_close_ratio"] = combined["spx_low"].shift(2) / combined["spx_close"].shift(2)

    #create column prev_vix_high, which is previous day's vix_high
    combined["vix_high_prev"] = combined["vix_high"].shift(1)

    #create column prev2_vix_high, which is previous-previous day's vix_high
    combined["vix_high_prev2"] = combined["vix_high"].shift(2)

    #create column prev_vix_close, which is previous day's vix_close
    combined["vix_close_prev"] = combined["vix_close"].shift(1)

    #create column prev2_vix_close, which is previous-previous day's vix_close
    combined["vix_close_prev2"] = combined["vix_close"].shift(2)

    # create column spx_close_20dma_ratio, which is the ratio
    # of current day's spx_close to current day's spx_close_20dma
    combined["spx_close_20dma_ratio"] = combined["spx_close"] / combined["spx_close_20dma"]

    #create column spx_prev_close_20dma_ratio, which is the ratio
    # of previous day's spx_close to previous day's spx_close_20dma
    combined["spx_prev_close_20dma_ratio"] = combined["spx_close"].shift(1) / combined["spx_close_20dma"].shift(1)

    #create column spx_prev2_close_20dma_ratio, which is the ratio
    # of previous-previous day's spx_close to previous-previous day's spx_close_20dma
    combined["spx_prev2_close_20dma_ratio"] = combined["spx_close"].shift(2) / combined["spx_close_20dma"].shift(2)

    # create column spx_close_200dma_ratio, which is the ratio
    # of current day's spx_close to current day's spx_close_200dma
    combined["spx_close_200dma_ratio"] = combined["spx_close"] / combined["spx_close_200dma"]

    # create column spx_prev_close_200dma_ratio, which is the ratio
    # of previous day's spx_close to previous day's spx_close_200dma
    combined["spx_prev_close_200dma_ratio"] = combined["spx_close"].shift(1) / combined["spx_close_200dma"].shift(1)

    # create column spx_prev2_close_200dma_ratio, which is the ratio
    # of previous-previous day's spx_close to previous-previous day's spx_close_200dma
    combined["spx_prev2_close_200dma_ratio"] = combined["spx_close"].shift(2) / combined["spx_close_200dma"].shift(2)  

    return combined

# For each day, determine if within the next days the SPX hits either
# target_pct percent higher or lower first
# create a new column 'target_direction' within combined to store the result,
# use 1 to designate hitting the higher target first,
# 0 to designate hitting the lower target first, and nan to designate neither target hit
# look ahead as many days as needed until one target is hit or end of data is reached
# do not limit the search by using max_lookahead_days
def compute_direction(combined: pd.DataFrame) -> pd.DataFrame:
    target_pct = 0.03  # 5%
    combined["target_direction"] = pd.NA

    for idx in combined.index:
        start_price = combined.at[idx, "spx_close"]
        target_up = start_price * (1 + target_pct)
        target_down = start_price * (1 - target_pct)

        # Look ahead from the next day onward
        lookahead_data = combined.loc[combined.index > idx]

        direction = pd.NA

        for _, row in lookahead_data.iterrows():
            if row["spx_high"] >= target_up and row["spx_low"] <= target_down:
                # If both targets are hit in the same day, consider it as no target hit
                # direction = pd.NA
                break
            if row["spx_high"] >= target_up:
                direction = 1
                break
            elif row["spx_low"] <= target_down:
                direction = 0
                break

        combined.at[idx, "target_direction"] = direction

    return combined



def prepare_features(combined: pd.DataFrame, features: list):
    X = combined[features].copy()
    y = combined["target_direction"].copy()

    # create a mask for just X's not na
    x_mask = X.notna().all(axis=1)
    mask = X.notna().all(axis=1) & y.notna()

    X_notna = X[x_mask]
    y_clean = y[mask].astype(int)

    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X_notna), columns=features, index=X_notna.index)
    X_clean = X_scaled.loc[mask]

    return X_scaled, X_clean, y_clean, scaler


def train_model(X_scaled: pd.DataFrame, X_clean: pd.DataFrame, y_clean: pd.Series):
    '''
    X_train, X_test, y_train, y_test = train_test_split(
        X_clean, y_clean, test_size=0.5, random_state=42, stratify=y_clean
    )
`   '''

    n = len(X_clean)
    split = n * 0.5  # 50% for training

    X_train = X_clean.iloc[:int(split)]
    X_test  = X_clean.iloc[int(split):]

    y_train = y_clean.iloc[:int(split)]
    y_test  = y_clean.iloc[int(split):]

    '''
    clf = RandomForestClassifier(
    n_estimators=350,          # more stable than 200
    max_depth=10,              # limits tree complexity
    min_samples_leaf=10,       # key overfit control
    min_samples_split=20,
    max_features="sqrt",
    class_weight="balanced",   # handles 70/30 imbalance
    oob_score=True,            # free validation signal
    n_jobs=-1,                 # use all 8 cores
    random_state=42
    )
    '''

    '''
    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=4,
        min_samples_leaf=100,
        max_features=0.3,
        class_weight="balanced",
    )

    '''
    clf = LogisticRegression(
        penalty="l2",
        C=0.1,
        class_weight="balanced",
        max_iter=2000
    )

    
    clf.fit(X_train, y_train)

    probs = clf.predict_proba(X_scaled)
    prob_df = pd.DataFrame(probs, columns=[f"P({c})" for c in clf.classes_], index=X_scaled.index)

    return clf, X_train, X_test, y_train, y_test, prob_df

# using a probability threshold for class 1 and 0
# evaluate training data for precision when P(1) >= threshold and P(0) >= threshold
# ignore cases where neither P(1) nor P(0) meets the threshold
# evaluate test data in the same way
def evaluate_and_print(clf, x_clean, y_clean, prob_df, x_test, y_test, x_train, y_train):
    from sklearn.metrics import classification_report

    threshold = 0.55

    # Evaluate on training data — align prob_df rows to x_train (same index)
    prob_train_df = prob_df.loc[x_train.index.intersection(prob_df.index)]
    train_mask = (prob_train_df["P(1)"] >= threshold) | (prob_train_df["P(0)"] >= threshold)
    y_train_filtered = y_clean.loc[train_mask.index][train_mask]
    train_pred = (prob_train_df.loc[train_mask, "P(1)"] >= threshold).astype(int)

    print("\n📊 TRAINING DATA CLASSIFICATION REPORT:")
    print(classification_report(y_train_filtered, train_pred, zero_division=0))

    # Evaluate on test data — align prob_df rows to x_test (same index)
    prob_test_df = prob_df.loc[x_test.index.intersection(prob_df.index)]
    test_mask = (prob_test_df["P(1)"] >= threshold) | (prob_test_df["P(0)"] >= threshold)
    y_test_filtered = y_test.loc[test_mask.index][test_mask]
    test_pred = (prob_test_df.loc[test_mask, "P(1)"] >= threshold).astype(int)

    print("\n📊 TEST DATA CLASSIFICATION REPORT:")
    print(classification_report(y_test_filtered, test_pred, zero_division=0))

'''
def predict_future_and_merge(combined: pd.DataFrame, features: list, scaler: StandardScaler, clf):
    future_mask = combined[features].notna().all(axis=1) & combined["target_direction"].isna()
    future_data = combined.loc[future_mask, features]
    future_prob_df = pd.DataFrame()

    if not future_data.empty:
        X_future_scaled = scaler.transform(future_data)
        future_pred_probs = clf.predict_proba(X_future_scaled)
        future_pred = clf.predict(X_future_scaled)

        future_prob_df = pd.DataFrame(
            future_pred_probs, columns=[f"P({c})" for c in clf.classes_], index=future_data.index
        )

        results_future = pd.concat(
            [
                combined.loc[future_mask, ["spx_high", "spx_low", "spx_close", "vix_high"]],
                future_prob_df,
                pd.Series(future_pred, index=future_data.index, name="prediction"),
            ],
            axis=1,
        )

        print("\n🟢 LATEST UNLABELED ROW PREDICTIONS (with full data):")
        print(results_future.tail(10))

    # Merge historical and future probabilities into combined
    # (prob_df is expected to be provided externally by caller)
    return future_prob_df
'''

# merge prob_df into combined on index
# also create a column in combined which designates if a row was a training row
# or not
def merge_probs_into_combined(combined: pd.DataFrame, prob_df: pd.DataFrame, x_train: pd.DataFrame) -> pd.DataFrame:
    combined = combined.merge(prob_df, left_index=True, right_index=True, how="left")
    combined["is_training"] = combined.index.isin(x_train.index)
    print("\n✅ Combined now contains probability columns:")
    print(combined.tail(20))
    return combined


# create an html page with 2 sub plots:
# that share an x-axis (date)
# top sub plot: SPX plot in OHLC format but with only spx_high, spx_low, spx_close
# if possible leave off the open portion of the OHLC bars
# bottom sub plot: bar plot probabilities based on a threshold of 0.6
# if P(1) >= 0.6, green bar for P(1) if its not a training row
# and a lighter shade green bar if it is a training row
# else if P(0) >= 0.6, red bar for P(0) if its not a training row
# and a lighter shade red bar if it is a training row
# else no bar
# make the plots zoomable, by default show last N days
# but double click would zoom out to show all days
def plot_results(combined: pd.DataFrame, N: int = 100, outpath: str = "spx_and_prob_stacked.html"):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    x = combined.index   # already sorted datetime index

    # ------------------------------------------------------------
    # 75% / 25% vertical split
    # ------------------------------------------------------------
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.75, 0.25],
    )

    # ============================================================
    # TOP – SPX H/L/C only (no open body)
    # ============================================================
    fig.add_trace(
        go.Candlestick(
            x=x,
            open=combined["spx_close"],   # open = close -> hide body
            high=combined["spx_high"],
            low=combined["spx_low"],
            close=combined["spx_close"],
            increasing_line_color="black",
            decreasing_line_color="black",
            showlegend=False,
            name="SPX",
        ),
        row=1,
        col=1,
    )

    # ============================================================
    # BOTTOM – probability bars with threshold
    # ============================================================
    threshold = 0.53
    green = "rgba(0,180,0,0.9)"
    light_green = "rgba(0,180,0,0.35)"
    red = "rgba(200,0,0,0.9)"
    light_red = "rgba(200,0,0,0.35)"

    values = []
    colors = []

    for _, r in combined.iterrows():
        p1 = r["P(1)"]
        p0 = r["P(0)"]
        train = r["is_training"]

        if p1 >= threshold:
            values.append(p1)
            colors.append(light_green if train else green)

        elif p0 >= threshold:
            values.append(-p0)      # red downward
            colors.append(light_red if train else red)

        else:
            values.append(0)
            colors.append("rgba(0,0,0,0)")

    fig.add_trace(
        go.Bar(
            x=x,
            y=values,
            marker_color=colors,
            showlegend=False,
            name="Probs",
        ),
        row=2,
        col=1,
    )

    # ------------------------------------------------------------
    # Default zoom = last N days
    # ------------------------------------------------------------
    if len(combined) > N:
        fig.update_xaxes(range=[x[-N], x[-1]], row=1, col=1)

    fig.update_layout(
        title="SPX + Model Probabilities",
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        height=820,
        margin=dict(l=40, r=20, t=40, b=30),
    )

    fig.update_yaxes(title="SPX", row=1, col=1)
    fig.update_yaxes(title="Probability", row=2, col=1, zeroline=True)

    # Native Plotly:
    # - drag/scroll zoom
    # - double click = reset to all

    fig.write_html(outpath, include_plotlyjs="cdn")
    return outpath

def main():
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 0)

    spx, vix = download_data()
    print("✅ Data downloaded.")
    combined = create_combined(spx, vix)
    print("✅ Combined DataFrame created.")
    combined = raw_features(combined)
    print("✅ Raw features computed.")
    combined = compute_direction(combined)
    print("✅ Target directions computed.")

    print(combined.head(20))
    print(combined.tail(20))

    features = ["vix_high", "vix_high_prev", "vix_high_prev2",
                "vix_close", "vix_close_prev", "vix_close_prev2",
                "spx_high_to_close_ratio", "spx_low_to_close_ratio",
                "spx_prev_close_to_high_ratio", "spx_prev_close_to_low_ratio",
                "spx_prev_high_to_close_ratio", "spx_prev_low_to_close_ratio",
                "spx_prev2_close_to_prev_high_ratio", "spx_prev2_close_to_prev_low_ratio",
                "spx_prev2_high_to_close_ratio", "spx_prev2_low_to_close_ratio",
                #"spx_close_20dma_ratio", "spx_prev_close_20dma_ratio", "spx_prev2_close_20dma_ratio",
                #"spx_close_200dma_ratio", "spx_prev_close_200dma_ratio", "spx_prev2_close_200dma_ratio"
               ]
    
    x_scaled, x_clean, y_clean, scaler = prepare_features(combined, features)
    print("✅ Features prepared.")

    clf, x_train, x_test, y_train, y_test, prob_df = train_model(x_scaled, x_clean, y_clean)
    print("✅ Model trained.")
    # print(clf.oob_score_)


    print(prob_df.head(50))
    print(prob_df.tail(50))

    evaluate_and_print(clf, x_clean, y_clean, prob_df, x_test, y_test, x_train, y_train)
    print("✅ Model evaluated.")

    combined = merge_probs_into_combined(combined, prob_df, x_train)
    print("✅ Probabilities merged into combined DataFrame.")

    plot_results(combined)
    print("✅ Results plotted.")

    '''
    features = ["vix_high", "vix_high_prev", "spx_high_pct_change", "spx_low_pct_change"]
    X_scaled, y_clean, scaler = prepare_features(combined, features)

    clf, X_train, X_test, y_train, y_test, prob_df = train_model(X_scaled, y_clean)

    evaluate_and_print(clf, X_scaled, y_clean, prob_df, X_test, y_test)

    future_prob_df = predict_future_and_merge(combined, features, scaler, clf)
    combined = merge_probs_into_combined(combined, prob_df, future_prob_df)

    plot_results(combined)
    '''

if __name__ == "__main__":
    main()
