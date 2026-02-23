import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, PROJECT_ROOT)

from src.data.data_scraper import *
from src.models.implied_vol import *


ticker = "NVDA"

S = get_spot_price(ticker)

r = get_risk_free_rate()

q = get_dividend_yield(ticker)

expiry = get_expiry_dates(ticker)[4]

T = time_to_expiry(expiry)

chain = get_option_chain(ticker, expiry)

print(expiry)
print(T)
# print(chain.columns)
# print(chain.head())

# ----------------------
# Calls Moneyness filter
# ----------------------
calls = chain[
    (chain["optionType"] == "call") &
    (chain["volume"] > 0)
].copy()

# Calculate moneyness
calls["moneyness"] = calls["strike"] / S

# Keep strikes between 0.8 and 1.2 moneyness
calls = calls[
    (calls["moneyness"] > 0.8) &
    (calls["moneyness"] < 1.6)
]

calls = calls.sort_values("strike").head(15)

# ----------------------
# Puts Moneyness filter
# ----------------------
puts = chain[
    (chain["optionType"] == "call") &
    (chain["volume"] > 0)
].copy()

# Calculate moneyness
puts["moneyness"] = puts["strike"] / S

# Keep strikes between 0.8 and 1.2 moneyness
puts = puts[
    (puts["moneyness"] > 0.8) &
    (puts["moneyness"] < 1.6)
]

puts = puts.sort_values("strike").head(15)



result_calls = implied_volatility_chain(
    calls,
    S,
    T,
    r,
    q,
    option_type="call"
)

result_puts = implied_volatility_chain(
    puts,
    S,
    T,
    r,
    q,
    option_type="put"
)

print(result_calls[["strike", "lastPrice", "impliedVol"]])
print(result_puts[["strike", "lastPrice", "impliedVol"]])