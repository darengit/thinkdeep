import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as pyo

# Download SPX and VIX data
spx = yf.download("^GSPC", start="1990-01-01")
vix = yf.download("^VIX", start="1990-01-01")

# Align both dataframes on dates (outer join)
combined = pd.DataFrame(index=spx.index)

# Add spx low/high prices
combined['spx_low'] = spx['Low']
combined['spx_high'] = spx['High']

# Add vix high/low/close prices reindexed to SPX dates (so aligned)
vix_reindexed = vix.reindex(combined.index)
combined['vix_high'] = vix_reindexed['High']
combined['vix_low'] = vix_reindexed['Low']
combined['vix_close'] = vix_reindexed['Close']

# Fill missing vix_high with most recent previous vix_close
combined['vix_close_filled'] = combined['vix_close'].fillna(method='ffill')
combined['vix_high_filled'] = combined['vix_high'].fillna(combined['vix_close_filled'])

# Fill missing vix_low similarly (for high band)
combined['vix_low_filled'] = combined['vix_low'].fillna(combined['vix_close_filled'])

# Drop dates where spx_low or spx_high is missing
combined = combined.dropna(subset=['spx_low', 'spx_high'])

# Calculate bands
combined['low_band'] = combined['spx_low'] * (1 + combined['vix_high_filled'] / 100 / 5)
combined['high_band'] = combined['spx_high'] * (1 + combined['vix_low_filled'] / 100 / 5)
combined['mid_band'] = (combined['low_band'] + combined['high_band']) / 2
combined['mid_band_20ma'] = combined['mid_band'].rolling(window=20).mean()

# Plot
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=combined.index,
    y=combined['low_band'],
    mode='lines',
    name='Low Band'
))
fig.add_trace(go.Scatter(
    x=combined.index,
    y=combined['high_band'],
    mode='lines',
    name='High Band'
))

'''
fig.add_trace(go.Scatter(
    x=combined.index,
    y=combined['mid_band'],
    mode='lines',
    name='Mid Band'
))
'''

fig.add_trace(go.Scatter(
    x=combined.index,
    y=combined['mid_band_20ma'],
    mode='lines',
    name='Mid Band 20-day MA'
))

fig.update_layout(
    title="SPX Bands with VIX Adjustments",
    xaxis_title="Date",
    yaxis_title="Value",
    xaxis_rangeslider_visible=True,
    yaxis=dict(autorange=True, fixedrange=False),  # key: fixedrange=False allows Y-axis to rescale on zoom
    dragmode="zoom"  # ensures zooming works
)

# Save HTML for WSL
pyo.plot(fig, filename='result.html', auto_open=False)
print("Plot saved as result.html")

