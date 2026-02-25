import os
import finnhub
import pandas as pd
from datetime import datetime

# set up client
# api_key = os.environ.get("FINHUB_API_KEY")
api_key = "d6eqru1r01qvn4o0nam0d6eqru1r01qvn4o0namg"
client = finnhub.Client(api_key=api_key)

def fetch_stock_data(symbol: str, start: str, end: str, resolution="D"):
    """
    symbol should be like "AAPL", "MSFT"
    start/end are YYYY-MM-DD strings
    resolution: one of D (daily), W, M, 1 (1 minute), etc.
    """
    # convert to unix timestamps
    dt_start = int(datetime.fromisoformat(start).timestamp())
    dt_end = int(datetime.fromisoformat(end).timestamp())

    # fetch data
    res = client.stock_candles(symbol, resolution, dt_start, dt_end)
    if res.get("s") != "ok":
        return pd.DataFrame()

    # build a DataFrame
    df = pd.DataFrame({
        "time": [datetime.fromtimestamp(ts) for ts in res["t"]],
        "open": res["o"],
        "high": res["h"],
        "low": res["l"],
        "close": res["c"],
        "volume": res["v"],
    })
    return df

df = fetch_stock_data("^DJI", "2025-01-01", datetime.now().strftime("%Y-%m-%d"))
print(df)