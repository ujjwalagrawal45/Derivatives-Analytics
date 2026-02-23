import pandas as pd
import numpy as np
import yfinance as yf
from pandas_datareader import data as pdr
import datetime
import streamlit as st

# -----------------------------------
# Historic Price Fetching
# -----------------------------------
def get_historical_data(ticker: str, period = "1y"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist


# -----------------------------------
# Fetch spot price of selected ticker
# -----------------------------------
def get_spot_price(ticker: str) -> float:
    stock = yf.Ticker(ticker)
    price = stock.history(period = "1d")["Close"].iloc[-1]
    return float(price)

# -----------------------
# Fetch historical OHLCV
# -----------------------
@st.cache_data
def get_historical_data(ticker: str, period = "1y") -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)

    hist.reset_index(inplace=True)

    return hist

# -----------------------------------
# Calculate histrical volatility
# -----------------------------------

def calculate_historical_volatility(ticker: str, window=30) -> float:

    hist = get_historical_data(ticker, period = "1y")

    hist["log_return"] = np.log(hist["Close"] / hist["Close"].shift(1))

    rolling_std = hist["log_return"].rolling(window=window).std()

    annualized_vol = rolling_std.iloc[-1] * np.sqrt(252)

    return float(annualized_vol)

# -----------------------------------
# Fetch dividend yield
# -----------------------------------

def get_dividend_yield(ticker: str) -> float:

    stock = yf.Ticker(ticker)

    info = stock.info
    
    if "dividendYield" in info and info["dividendYield"] is not None:
        return float(info["dividendYield"])
    
    return 0.0

# -----------------------------------
# Fetch option chain
# -----------------------------------
st.cache_data
def get_option_chain(ticker: str, expiry_date: str):

    stock = yf.Ticker(ticker)

    options = stock.option_chain(expiry_date)

    calls = options.calls.copy()
    puts = options.puts.copy()

    # Add explicit option type column
    calls["optionType"] = "call"
    puts["optionType"] = "put"

    combined = pd.concat([calls, puts], ignore_index=True)

    return combined

# --------------------------------------
# Fetch risk-free rate from FRED
# Using 3-month T-BilL (DGS3MO) as proxy
# --------------------------------------

def get_risk_free_rate() -> float:
    """
    Fetch 3-month T-Bill rate from FRED
    Falls back to constant rate if connection fails
    """

    import datetime

    try:
        end = datetime.datetime.today()
        start = end - datetime.timedelta(days=30)

        treasury = yf.Ticker("^IRX") # 13 week T-Bill index
        # rates = pdr.DataReader(
        #     "DGS3MO",
        #     "fred",
        #     start,
        #     end
        # )

        rates = treasury.history(period="1d")["Close"] # removing .iloc[-1] now and adding it to latest rates

        latest_rate = rates.iloc[-1, 0]

        if pd.isna(latest_rate):
            raise ValueError("Invalid rate received")
        
        return float(latest_rate) / 100
    
    except Exception as e:

        print("Warning: Could not reach FRED database. Using fallback rate.")
        # print("Error:", e)

        # Fallback rate based on recent historical average of 3-month T-Bill yield
        return 0.0425 

# -----------------------------------
# Get available expirations
# -----------------------------------
@st.cache_data
def get_expiry_dates(ticker: str):

    stock = yf.Ticker(ticker)

    return stock.options

# -----------------------------------
# Get time to expiry
# -----------------------------------
def time_to_expiry(expiry_date):

    import datetime

    today = datetime.datetime.today()
    expiry = datetime.datetime.strptime(expiry_date, "%Y-%m-%d")

    T = (expiry - today).days / 365

    return max(T, 0.0001)

# -----------------------------------
# Master function to fetch all inputs
# -----------------------------------
def get_all_inputs(ticker: str):

    return {
        "spot_price": get_spot_price(ticker),
        "hist_vol_30d": calculate_historical_volatility(ticker, window=30),
        "hist_vol_60d": calculate_historical_volatility(ticker, window=60),
        "dividend_yield": get_dividend_yield(ticker),
        "risk_free_rate": get_risk_free_rate(),
        "expiries": get_expiry_dates(ticker)
    }