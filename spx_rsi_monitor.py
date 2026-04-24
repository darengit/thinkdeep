import pandas as pd
import yfinance as yf
import time
import subprocess


def fetch_spx_levels(max_retries=5):
    for attempt in range(max_retries):
        try:
            spx = yf.Ticker("^GSPC")
            data = spx.history(period="1d", interval="1m")

            if data.empty:
                raise ValueError("Empty dataframe from yfinance")

            if "Close" not in data:
                raise ValueError("Missing Close column")

            spx_levels = data["Close"].dropna()

            if spx_levels.empty:
                raise ValueError("Close series empty after dropna")

            return spx_levels

        except Exception as e:
            print(f"[Attempt {attempt+1}] fetch failed: {e}")

            if attempt == max_retries - 1:
                raise

            # Exponential backoff before retrying
            # Sleep for 100 seconds on the first retry,
            # 200 seconds on the second, etc.
            time.sleep(100 * (attempt + 1))


def alert(message):
    # create a windows toast notification with the given message
    cmd = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null;
    $template = [Windows.UI.Notifications.ToastTemplateType]::ToastText02;
    $xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent($template);
    $textNodes = $xml.GetElementsByTagName('text');
    $textNodes.Item(0).AppendChild($xml.CreateTextNode('{message}')) > $null;
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml);
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('SPX RSI Monitor');
    $notifier.Show($toast);
    """

    subprocess.run(["powershell.exe", "-Command", cmd])


# use spx_levels to compute the 14 sample rsi
# spx_levels is a pandas.core.series.Series of the last 15 spx levels,
# with the most recent level at the end of the series
def compute_rsi(spx_levels: pd.Series) -> float:
    if len(spx_levels) < 15:
        return None

    # compute the price changes
    deltas = spx_levels.diff().dropna()

    # separate gains and losses
    gains = deltas.where(deltas > 0, 0)
    losses = -deltas.where(deltas < 0, 0)

    # compute the average gain and loss
    avg_gain = gains.rolling(window=14).mean().iloc[-1]
    avg_loss = losses.rolling(window=14).mean().iloc[-1]

    # compute the relative strength
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss

    # compute the RSI
    rsi = 100 - (100 / (1 + rs))
    return rsi

# alternative implementation of the RSI using Wilder's smoothing method
# this method is more accurate and is the one used by most technical analysts
# it uses an exponential moving average instead of a simple moving average to compute the average gain and loss
# the first 14 samples are used to compute the initial average gain and loss, and then the subsequent samples are used to update the average gain and loss using Wilder's smoothing method
# this method is more computationally efficient than the simple moving average method, as it does not require recomputing the average gain and loss for each new sample

def wilder_rsi(spx_levels: pd.Series) -> float:
    period = 14

    # Price changes
    delta = spx_levels.diff()

    # Separate gains and losses
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder’s smoothing (RMA)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    # Relative Strength
    rs = avg_gain / avg_loss

    # RSI
    rsi_series = 100 - (100 / (1 + rs))

    return float(rsi_series.iloc[-1])

# in an infinite loop,
# retrieve the current spx level every minute and compute the rsi
while True:
    # retrieve the current spx level
    spx_levels = fetch_spx_levels()

    # compute the 14-sample RSI
    rsi = wilder_rsi(spx_levels)
    print(rsi)

    # if rsi is either above 70 or below 30, create an alert for windows
    if rsi is not None and (rsi > 70 or rsi < 30):
        alert_message = f"SPX RSI Alert: RSI is at {rsi:.2f}"
        alert(alert_message)

    # sleep for 60 seconds before the next check
    time.sleep(60)
