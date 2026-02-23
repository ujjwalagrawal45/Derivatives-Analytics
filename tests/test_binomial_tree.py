import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, PROJECT_ROOT)

from src.models.binomial_tree import *


# Test parameters
S = 100
K = 100
T = 1
r = 0.05
sigma = 0.2


# European call
price_eur = binomial_option_price(
    S, K, T, r, sigma,
    steps=100,
    option_type="call",
    american=False
)

# American put
price_am = binomial_option_price(
    S, K, T, r, sigma,
    steps=100,
    option_type="put",
    american=True
)

print("European Call:", price_eur)

print("American Put:", price_am)


# Tree test
tree = generate_stock_tree(
    S, T, sigma, steps=50
)

print("\nStock Tree:")
for level in tree:
    print([round(float(x),2) for x in level])