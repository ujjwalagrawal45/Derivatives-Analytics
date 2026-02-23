import numpy as np
import pandas as pd

from src.models.black_scholes import black_scholes_price
from src.models.binomial_tree import binomial_option_price


def compare_models(
    options_df,
    S,
    T,
    r,
    q=0.0,
    steps=200,
    option_type="call"
):

    results = []

    for _, row in options_df.iterrows():

        strike = row["strike"]

        # Use mid-price
        if row["bid"] > 0 and row["ask"] > 0:
            market_price = (row["bid"] + row["ask"]) / 2
        else:
            market_price = row["lastPrice"]

        iv = row["impliedVol"]

        if np.isnan(iv):
            continue

        # Black–Scholes (European)
        bs_price = black_scholes_price(
            S, strike, T, r, iv, q, option_type
        )

        # Binomial (American)
        bin_price = binomial_option_price(
            S, strike, T, r, iv, q,
            steps=steps,
            option_type=option_type,
            american=True
        )

        results.append({
            "strike": strike,
            "market": market_price,
            "black_scholes": bs_price,
            "binomial": bin_price,
            "bs_error": bs_price - market_price,
            "binomial_error": bin_price - market_price
        })

    return pd.DataFrame(results)