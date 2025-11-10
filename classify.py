import yfinance as yf
import pandas as pd


from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pandas as pd



# Download SPX and VIX data
spx = yf.download("^GSPC", start="1990-01-01")
vix = yf.download("^VIX", start="1990-01-01")

# Create combined dataframe using SPX dates
combined = pd.DataFrame(index=spx.index)

# Add SPX columns
combined["spx_high"] = spx["High"]
combined["spx_low"] = spx["Low"]
combined["spx_close"] = spx["Close"]

# Reindex VIX to SPX calendar for alignment
vix_reindexed = vix.reindex(combined.index)

# Extract VIX values
combined["vix_high"] = vix_reindexed["High"]
combined["vix_close"] = vix_reindexed["Close"]

# Forward-fill VIX close first (so it always has a value)
combined["vix_close"] = combined["vix_close"].ffill()

# Fill missing vix_high using the most recent vix_close
combined["vix_high"] = combined["vix_high"].fillna(combined["vix_close"])

# Drop temporary vix_close if you no longer need it
combined = combined.drop(columns=["vix_close"])

# Drop any rows without SPX data
combined = combined.dropna(subset=["spx_high", "spx_low", "spx_close"])

# Create percent change columns for SPX high/low
combined["spx_high_pct_change"] = combined["spx_high"].pct_change()
combined["spx_low_pct_change"] = combined["spx_low"].pct_change()

# Create previous day's VIX high (shift by 1 row)
combined["vix_high_prev"] = combined["vix_high"].shift(1)


# Get previous day's values
combined["spx_low_prev"] = combined["spx_low"].shift(1)
combined["spx_high_prev"] = combined["spx_high"].shift(1)

# Compute 2-day low/high
combined["two_day_low"] = combined[["spx_low", "spx_low_prev"]].min(axis=1)
combined["two_day_high"] = combined[["spx_high", "spx_high_prev"]].max(axis=1)

# Difference from the close
combined["target_up"] = combined["two_day_high"] - combined["spx_close"]
combined["target_down"] = combined["spx_close"] - combined["two_day_low"]

# Determine overall target size
combined["target_move"] = combined[["target_up", "target_down"]].max(axis=1)

# ------------------------------------------------
# Determine first hit direction (your new logic)
# ------------------------------------------------

direction = []
n = len(combined)

for i in range(n):

    up_target = combined["two_day_high"].iloc[i]
    down_target = combined["two_day_low"].iloc[i]

    result = None

    # Scan every future day until one target is hit
    for j in range(i + 1, n):

        future_high = combined["spx_high"].iloc[j]
        future_low = combined["spx_low"].iloc[j]

        up_hit = future_high >= up_target
        down_hit = future_low <= down_target

        if up_hit and down_hit:
            result = 0  # both hit same day
            break
        elif up_hit:
            result = 1  # upside hit first
            break
        elif down_hit:
            result = -1  # downside hit first
            break

    direction.append(result)

combined["target_direction"] = direction



# show all columns
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 0)


print(combined.head(20))

print(combined.tail(20))

# Select features and target
features = ["vix_high", "vix_high_prev", "spx_high_pct_change", "spx_low_pct_change"]
X = combined[features].copy()
y = combined["target_direction"].copy()

# Remove rows where any feature or target is None/NaN
mask = X.notna().all(axis=1) & y.notna()
X_clean = X[mask]
y_clean = y[mask]

# Standardize all features together
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_clean)

# Convert back to DataFrame for convenience
X_scaled = pd.DataFrame(X_scaled, columns=features, index=X_clean.index)

# Quick check
print(X_scaled.describe())
print(y_clean.value_counts())


X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_clean, test_size=0.5, random_state=42, stratify=y_clean
)
clf = RandomForestClassifier(n_estimators=200, random_state=42)
clf.fit(X_train, y_train)
probs = clf.predict_proba(X_scaled)

prob_df = pd.DataFrame(probs, columns=[f"P({c})" for c in clf.classes_], index=X_scaled.index)
results = pd.concat([X_scaled, y_clean, prob_df], axis=1)
print(results.head())


'''
from sklearn.metrics import log_loss

# Reorder columns to match class order [-1, 0, 1]
prob_df_ordered = prob_df[[-1,0,1]] if -1 in prob_df.columns else prob_df[['P(-1)','P(0)','P(1)']]
prob_array = prob_df_ordered.values

# Map y_clean to 0/1/2 indices corresponding to columns
class_to_idx = {-1:0, 0:1, 1:2}
y_indices = y_clean.map(class_to_idx).values

loss = log_loss(y_indices, prob_array)
print(f"Log Loss: {loss:.4f}")
'''



# Map desired order [-1, 0, 1] to actual column names
desired_order = [-1, 0, 1]
column_map = {float(c): f"P({c})" for c in [-1.0, 0.0, 1.0]}  # matches your float columns

# Reorder prob_df
prob_df_ordered = prob_df[[column_map[c] for c in [-1.0, 0.0, 1.0]]]
print(prob_df_ordered.head())


from sklearn.metrics import log_loss

# Map target to indices: -1 -> 0, 0 -> 1, 1 -> 2
class_to_idx = {-1: 0, 0: 1, 1: 2}
y_indices = y_clean.map(class_to_idx).values

# Compute log-loss
loss = log_loss(y_indices, prob_df_ordered.values)
print(f"Log Loss: {loss:.4f}")


from sklearn.metrics import accuracy_score

y_pred_class = prob_df_ordered.idxmax(axis=1).str.extract(r'(-?\d+)').astype(int)[0]
acc = accuracy_score(y_clean, y_pred_class)
print(f"Accuracy: {acc:.4f}")


# Predict probabilities for X_test
probs_test = clf.predict_proba(X_test)

# Create a DataFrame with class probabilities
prob_test_df = pd.DataFrame(probs_test, columns=[f"P({c})" for c in clf.classes_], index=X_test.index)


# Predicted class = argmax of probabilities
y_pred_test = prob_test_df.idxmax(axis=1).str.extract(r'(-?\d+)').astype(int)[0]


from sklearn.metrics import accuracy_score

acc_test = accuracy_score(y_test, y_pred_test)
print(f"Test Accuracy: {acc_test:.4f}")


from sklearn.metrics import log_loss

# Map target to indices for log loss
class_to_idx = {-1: 0, 0: 1, 1: 2}
y_test_indices = y_test.map(class_to_idx).values

# Reorder columns to [-1,0,1] for log loss
prob_test_df_ordered = prob_test_df[[f"P({c})" for c in [-1.0,0.0,1.0]]]

logloss_test = log_loss(y_test_indices, prob_test_df_ordered.values)
print(f"Test Log Loss: {logloss_test:.4f}")


threshold = 0.9

# Find rows where any probability exceeds threshold
confident_mask = (prob_test_df[['P(-1.0)','P(0.0)','P(1.0)']] >= threshold).any(axis=1)

# Subset test set
X_confident = X_test[confident_mask]
y_confident = y_test[confident_mask]
prob_confident = prob_test_df[confident_mask]


# Predicted class = argmax of probabilities
y_pred_confident = prob_confident.idxmax(axis=1).str.extract(r'(-?\d+)').astype(int)[0]


from sklearn.metrics import accuracy_score, log_loss

# Accuracy
acc_confident = accuracy_score(y_confident, y_pred_confident)
print(f"Accuracy on confident predictions: {acc_confident:.4f}")

# Log loss
class_to_idx = {-1:0, 0:1, 1:2}
y_indices_confident = y_confident.map(class_to_idx).values

# Reorder columns [-1,0,1] for log loss
prob_confident_ordered = prob_confident[['P(-1.0)','P(0.0)','P(1.0)']]

logloss_confident = log_loss(y_indices_confident, prob_confident_ordered.values)
print(f"Log Loss on confident predictions: {logloss_confident:.4f}")



print(f"Total test rows: {len(y_test)}")
print(f"Rows with probability >= {threshold}: {len(y_confident)} ({len(y_confident)/len(y_test)*100:.2f}%)")



# Distribution of actual target directions when the threshold is hit
direction_counts = y_confident.value_counts()
direction_percent = y_confident.value_counts(normalize=True) * 100

print("Counts of actual directions when threshold is hit:")
print(direction_counts)
print("\nPercentage of each direction:")
print(direction_percent)



import pandas as pd

# Combine actual and predicted for convenience
conf_df = pd.DataFrame({
    "actual": y_confident,
    "predicted": y_pred_confident
})

# Count total instances per actual class
total_per_class = conf_df['actual'].value_counts()

# Count correct predictions per class
correct_per_class = (conf_df['actual'] == conf_df['predicted']).groupby(conf_df['actual']).sum()

# Compute per-class accuracy
accuracy_per_class = correct_per_class / total_per_class

print("Per-class accuracy for confident predictions:")
print(accuracy_per_class)

# Also show counts and percentages of actual labels
counts = conf_df['actual'].value_counts()
percent = conf_df['actual'].value_counts(normalize=True) * 100
print("\nCounts of actual directions when threshold is hit:")
print(counts)
print("\nPercentage of each direction:")
print(percent)





# ------------------------------------
# PREDICT FUTURE (label = NaN)
# ------------------------------------
future_mask = combined[features].notna().all(axis=1) & combined["target_direction"].isna()
future_data = combined.loc[future_mask, features]

X_future_scaled = scaler.transform(future_data)
future_pred_probs = clf.predict_proba(X_future_scaled)
future_pred = clf.predict(X_future_scaled)

# Convert predicted probabilities to DataFrame
future_prob_df = pd.DataFrame(
    future_pred_probs,
    columns=[f"P({c})" for c in clf.classes_],
    index=future_data.index
)

# Build final output with ALL requested data
results_future = pd.concat(
    [
        combined.loc[future_mask, ["spx_high", "spx_low", "spx_close", "vix_high"]],
        future_prob_df,
        pd.Series(future_pred, index=future_data.index, name="prediction"),
    ],
    axis=1
)

print("\n🟢 LATEST UNLABELED ROW PREDICTIONS (with full data):")
print(results_future.tail(10))

# ------------------------------------
# MERGE prob_df + future_prob_df into combined
# ------------------------------------

# Combine historical predictions with future predictions
prob_all = pd.concat([prob_df, future_prob_df], axis=0)

# Merge into main dataset
combined = combined.merge(prob_all, left_index=True, right_index=True, how="left")

# Optional cleanup of column names
combined.rename(columns={
    "P(-1.0)": "P(-1)",
    "P(0.0)" : "P(0)",
    "P(1.0)" : "P(1)"
}, inplace=True)

print("\n✅ Combined now contains probability columns:")
print(combined.tail(10))








import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Filter valid rows
plot_data = combined.dropna(subset=["spx_close", "P(1)"])

# Optionally limit to last N rows
N = 100
plot_data = plot_data.tail(N)

# Create subplots: 2 rows, shared x-axis
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.1,
    row_heights=[0.75, 0.25]  # top bigger than bottom
)

# Top: SPX Close
fig.add_trace(
    go.Scatter(x=plot_data.index, y=plot_data["spx_close"], 
               mode="lines", name="SPX Close", line=dict(color="blue")),
    row=1, col=1
)

# Bottom: P(1) as bars
fig.add_trace(
    go.Bar(x=plot_data.index, y=plot_data["P(1)"], 
           name="P(1)", marker_color="green", opacity=0.6),
    row=2, col=1
)

# Layout settings
fig.update_layout(
    title=f"SPX Close (top) and P(1) Probability (bottom) — Last {N} Days",
    xaxis2=dict(title="Date"),  # bottom x-axis label
    yaxis=dict(title="SPX Close"),
    yaxis2=dict(title="P(1)"),
    height=600
)

# Save to HTML for WSL
fig.write_html("spx_and_p1_stacked.html")
print("✅ Stacked plot saved as spx_and_p1_stacked.html")














