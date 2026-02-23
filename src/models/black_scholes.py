import numpy as np
from scipy.stats import norm

# -----------------------------------
# Internal d1 and d2 calculations
# -----------------------------------
def _compute_d1_d2(S, K, T, r, sigma, q):

    if T <= 0 or sigma <= 0:
        raise ValueError("T and sigma must be +ive")
    
    d1 = (
        np.log(S / K)
        + (r - q + 0.5 * sigma ** 2) * T
    ) / (sigma * np.sqrt(T)) 

    d2 = d1 - sigma * np.sqrt(T)

    return d1, d2

# -----------------------------------
# Option price
# -----------------------------------
def black_scholes_price(
    S,
    K,
    T,
    r,
    sigma,
    q = 0.0,
    option_type = "call"
):
    
    d1, d2 = _compute_d1_d2(S, K, T, r, sigma, q)

    if option_type.lower() == "call":

        price = (
            S * np.exp(-q * T) * norm.cdf(d1)
            - K * np.exp(-r * T) * norm.cdf(d2)
        )

    elif option_type.lower() == "put":

        price = (
            S * np.exp(-r * T) * norm.cdf(-d2)
            - K * np.exp(-q * T) * norm.cdf(-d1)
        )

    else:
        raise ValueError("option type must be call or put")
    
    return float(price)

# -----------------------------------
# Greeks Calculations
# -----------------------------------
def black_scholes_greeks(
    S,
    K,
    T,
    r,
    sigma,
    q = 0.0,
    option_type = "call"
):
    
    d1, d2 = _compute_d1_d2(S, K, T, r, sigma, q)

    pdf_d1 = norm.pdf(d1)

    # Delta
    if option_type.lower() == "call":
        delta = np.exp(-q * T) * norm.cdf(d1)
    else:
        delta = np.exp(-q * T) * (norm.cdf(d1) - 1)

    # Gamma
    gamma = (
        np.exp(-q * T)
        * pdf_d1
        / (S * sigma * np.sqrt(T))
    )

    # Vega
    vega = (
        S
        * np.exp(-q * T)
        * pdf_d1
        * np.sqrt(T)
    )

    # Theta
    term1 = (
        -S
        * pdf_d1
        * sigma
        * np.exp(-q * T)
        / (2 * np.sqrt(T))
    )

    if option_type.lower() == "call":

        theta = (
            term1
            - r * K * np.exp(-r * T) * norm.cdf(d2)
            + q * S * np.exp(-q * T) * norm.cdf(d1)
        )

    else:

        theta = (
            term1
            + r * K * np.exp(-r * T) * norm.cdf(-d2)
            - q * S * np.exp(-q * T) * norm.cdf(-d1)
        )

    # Rho
    if option_type.lower() == "call":

        rho = (
            K
            * T
            * np.exp(-r * T)
            * norm.cdf(d2)
        )
    
    else:

        rho = (
            -K
            * T
            * np.exp(-r * T)
            * norm.cdf(-d2)
        )

    return {
        "delta": float(delta),
        "gamma": float(gamma),
        "vega": float(vega),
        "theta": float(theta),
        "rho": float(rho)
    }

# -----------------------------------
# Convenience wrapper
# -----------------------------------

def price_and_greeks(
        S, K, T, r, sigma, q = 0.0,
        option_type="call"
):
    
    price = black_scholes_price(
        S, K, T, r, sigma, q, option_type
    )

    greeks = black_scholes_greeks(
        S, K, T, r, sigma, q, option_type
    )

    return {
        "price": price,
        **greeks
    }