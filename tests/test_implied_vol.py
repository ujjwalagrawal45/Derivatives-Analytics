import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, PROJECT_ROOT)

from src.models.black_scholes import *
from src.models.implied_vol import *


# Known parameters
S = 100
K = 100
T = 1
r = 0.05
sigma_true = 0.2


# Generate market price
market_price = black_scholes_price(
    S, K, T, r, sigma_true, option_type="call"
)

print("Market Price:", market_price)


# Solve implied volatility
iv = implied_volatility(
    market_price,
    S,
    K,
    T,
    r,
    option_type="call"
)

print("Recovered IV:", iv)