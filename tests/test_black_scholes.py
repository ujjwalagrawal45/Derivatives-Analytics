import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.models.black_scholes import *

# Test parameters
S = 100
K = 120
T = 1
r = 0.05
sigma = 0.2
q = 0.0

print("call price:",
      black_scholes_price(S, K, T, r, sigma, q, "call"))
print("put price:",
      black_scholes_price(S, K, T, r, sigma, q, "put"))

print("Greeks:",
      black_scholes_greeks(S, K, T, r, sigma, q, "call"))
print("Greeks:",
      black_scholes_greeks(S, K, T, r, sigma, q, "put"))