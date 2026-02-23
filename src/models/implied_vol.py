import numpy as np

from src.models.black_scholes import (
    black_scholes_price,
    black_scholes_greeks
)


# ----------------------------
# Newton-Raphson Solver
# ----------------------------
def implied_volatility(
    market_price,
    S,
    K,
    T,
    r,
    q=0.0,
    option_type="call",
    initial_guess=0.2,
    tolerance=1e-6,
    max_iterations=100
):

    sigma = initial_guess

    for i in range(max_iterations):

        price = black_scholes_price(
            S, K, T, r, sigma, q, option_type
        )

        greeks = black_scholes_greeks(
            S, K, T, r, sigma, q, option_type
        )

        vega = greeks["vega"]

        diff = price - market_price

        # Convergence check
        if abs(diff) < tolerance:
            return float(sigma)

        # Avoid division by zero
        if vega < 1e-8:
            break

        # Newton-Raphson update
        sigma = sigma - diff / vega

        if sigma <= 0:
            sigma = 0.0001
        
        if sigma > 5:
            sigma = 5    

    raise RuntimeError(
        "Implied volatility did not converge"
    )


# ----------------------------
# Batch solver for options chain
# ----------------------------
def implied_volatility_chain(
    options_df,
    S,
    T,
    r,
    q=0.0,
    option_type="call"
):

    iv_list = []

    for _, row in options_df.iterrows():

        strike = row["strike"]

        # Use mid-price instead of last trade
        if row["bid"] > 0 and row["ask"] > 0:
            market_price = (row["bid"] + row["ask"]) / 2
        else:
            market_price = row["lastPrice"]

        # ----------------------------
        # No-arbitrage intrinsic check
        # ----------------------------
        if option_type.lower() == "call":
            intrinsic = max(S - strike, 0)
        else:
            intrinsic = max(strike - S, 0)

        # If price violates arbitrage bound → no IV
        if market_price < intrinsic:
            iv_list.append(np.nan)
            continue

        try:
            iv = implied_volatility(
                market_price,
                S,
                strike,
                T,
                r,
                q,
                option_type
            )
        except:
            iv = np.nan

        iv_list.append(iv)

    options_df = options_df.copy()
    options_df["impliedVol"] = iv_list

    return options_df