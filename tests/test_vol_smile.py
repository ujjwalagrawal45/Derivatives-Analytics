import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.insert(0, PROJECT_ROOT)

from src.data.data_scraper import *
from src.models.implied_vol import *
from src.visualizations.plots import *


ticker = "NVDA"

S = get_spot_price(ticker)
r = get_risk_free_rate()
q = get_dividend_yield(ticker)

expiries = get_expiry_dates(ticker)

# choose a stable expiry (not nearest)
expiry = expiries[3]

T = time_to_expiry(expiry)

chain = get_option_chain(ticker, expiry)

calls = chain[
    (chain["optionType"] == "call") &
    (chain["volume"] > 0)
].copy()

# moneyness filter
calls["moneyness"] = calls["strike"] / S
calls = calls[
    (calls["moneyness"] > 0.8) &
    (calls["moneyness"] < 1.2)
]

result = implied_volatility_chain(
    calls,
    S,
    T,
    r,
    q,
    option_type="call"
)

fig = plot_volatility_smile(result, ticker, expiry)

fig.show()