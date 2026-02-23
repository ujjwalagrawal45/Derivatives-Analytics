import sys
import os

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.data.data_scraper import *

ticker = "NVDA"

print("Spot:", get_spot_price(ticker))

print("Vol 30d:", calculate_historical_volatility(ticker, 30))

print("Dividend yield:", get_dividend_yield(ticker))

print("Risk-free rate:", get_risk_free_rate())

expiries = get_expiry_dates(ticker)

print("Expiries:", expiries[:5])

chain = get_option_chain(ticker, expiries[0])

print(chain.head())
