import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.subplots import make_subplots
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

# Download SPX and VIX data
spx = yf.download("^GSPC", start="1990-01-01")
vix = yf.download("^VIX", start="1990-01-01")

# Align both dataframes on dates (outer join)
combined = pd.DataFrame(index=spx.index)

# columns with an spx_close but no vix_close,
# forward fill vix_close with the most recent previous vix_close value
combined["spx_close"] = spx["Close"]
combined["vix_close"] = vix["Close"].reindex(combined.index).ffill()

# drop rows where spx_close is missing
combined = combined.dropna(subset=["spx_close"])

# create a column day_of_week, where Monday is -2 and friday is 2, 
# and 0 is the middle of the week
combined["day_of_week"] = combined.index.dayofweek - 2

# adjust vix_close by (day_of_week * 0.5) percent,
# so that vix_close is lower on mondays and higher on fridays
combined["vix_close_adjusted"] = combined["vix_close"] * (1 + combined["day_of_week"] * 0.005)

'''
# print statistics on vix_close_adjusted by day of week
stats = combined.groupby("day_of_week")["vix_close_adjusted"].agg(["mean", "median", "std"])
print(stats)
'''

# make a column called spx_return
# which is the percentage return of spx_close from yesterday to today
combined["spx_return"] = combined["spx_close"].pct_change()

# make a column called vix_close_adjusted_prev
# which is the vix_close_adjusted value from the previous day
combined["vix_close_adjusted_prev"] = combined["vix_close_adjusted"].shift(1)

# create a column called quadratic fit
# which is the result of a quadratic fit of spx_return
# as a function of vix_close_adjusted and vix_close_adjusted_prev

# drop rows with missing values
combined = combined.dropna(subset=["spx_return", "vix_close_adjusted", "vix_close_adjusted_prev"])
X = combined[["vix_close_adjusted", "vix_close_adjusted_prev"]]
y = combined["spx_return"]
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
model = LinearRegression()
model.fit(X_poly, y)
combined["quadratic_fit"] = model.predict(X_poly)

# make a scatter plot with spx_return on the z axis
# vix_close_adjusted on the x axis
# and vix_close_adjusted_prev on the y axis
# superimpose upon this scatter plot combined["quadratic_fit"]
# as a surface plot

# original data
x = combined["vix_close_adjusted"].values
y = combined["vix_close_adjusted_prev"].values
z = combined["spx_return"].values

# create grid
x_grid = np.linspace(x.min(), x.max(), 50)
y_grid = np.linspace(y.min(), y.max(), 50)
X_grid, Y_grid = np.meshgrid(x_grid, y_grid)

# evaluate your fitted model on the grid
# assuming you already trained `model` with PolynomialFeatures
XY_grid = np.column_stack([X_grid.ravel(), Y_grid.ravel()])
XY_grid_poly = poly.transform(XY_grid)
Z_grid = model.predict(XY_grid_poly).reshape(X_grid.shape)

# plot
fig = go.Figure(data=[
    go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(size=5, color=z, colorscale='Viridis', opacity=0.8)
    ),
    go.Surface(
        x=X_grid,
        y=Y_grid,
        z=Z_grid,
        colorscale='Viridis',
        opacity=0.5,
        showscale=False
    )
])

fig.update_layout(
    title='SPX Return vs VIX Close Adjusted',
    scene=dict(
        xaxis_title='VIX Close Adjusted',
        yaxis_title='VIX Close Adjusted Previous Day',
        zaxis_title='SPX Return'
     )
)

pyo.plot(fig, filename='spx_vix_close_3d.html')

print(combined[["vix_close_adjusted", "vix_close_adjusted_prev", "spx_return", "quadratic_fit"]].tail())

# create a column called residual
# which is the difference between spx_return and quadratic_fit
combined["residual"] = combined["spx_return"] - combined["quadratic_fit"]

# create a column which is the 5 day moving average of the residual
combined["residual_5dma"] = combined["residual"].rolling(window=5).mean()

# create an html page with 2 stacked plots, top and bottom
# on the top plot plot spx_close
# on the bottom plot, separate y-axis from the top plot
# plot each residual
# as thick vertical bars, use a green bar for positive values
# and a red bar for negative values
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05
)

# Top plot: SPX Close
fig.add_trace(
    go.Scatter(
        x=combined.index,
        y=combined["spx_close"],
        mode='lines',
        name='SPX Close'
    ),
    row=1, col=1
)

# Bottom plot: residual as bars
residual = combined["residual"]

fig.add_trace(
    go.Bar(
        x=combined.index,
        y=residual,
        name='Residual',
        marker_color=np.where(residual > 0, 'green', 'red')
    ),
    row=2, col=1
)

# also add residual_5dma as a line plot on the same bottom plot
# with the same y-axis as the residual bars
# but with a different color and a legend entry
fig.add_trace(
    go.Scatter(
        x=combined.index,
        y=combined["residual_5dma"],
        mode='lines',
        name='Residual 5DMA',
        line=dict(color='black')
     ),
     row=2, col=1
)


# Layout
fig.update_layout(
    title='SPX Close and Residual',
    xaxis_title='Date'
)

# Optional: label y-axes separately
fig.update_yaxes(title_text='SPX Close', row=1, col=1)
fig.update_yaxes(title_text='Residual', row=2, col=1)

pyo.plot(fig, filename='spx_vix_close_residuals.html')


print(combined[["spx_close", "spx_return", "quadratic_fit", "residual"]].tail(50))