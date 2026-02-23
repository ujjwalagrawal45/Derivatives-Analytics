import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
import numpy as np

from src.data.data_scraper import *
from src.models.black_scholes import *
from src.models.binomial_tree import *
from src.models.implied_vol import *
from src.analysis.model_comparison import *
from src.visualizations.plots import *
from src.models.monte_carlo import monte_carlo_option_price


# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(layout="wide")

st.title("Derivatives Analytics Platform")
st.caption(
    "Black–Scholes | Binomial Tree | Monte Carlo | Volatility Surface | Risk Analytics"
)


# ---------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------
page = st.sidebar.radio(
    "Navigation",
    [
        "Market Overview",
        "Option Pricing",
        "Risk & Greeks",
        "Volatility Analytics"
    ]
)

st.sidebar.header("Option Inputs")

ticker = st.sidebar.text_input("Ticker", "NVDA")

if not ticker:
    st.stop()

expiries = get_expiry_dates(ticker)

expiry = st.sidebar.selectbox("Expiry", expiries)

strike = st.sidebar.number_input(
    "Strike",
    value=float(round(get_spot_price(ticker)))
)

option_type = st.sidebar.selectbox(
    "Option Type",
    ["call", "put"]
)

steps = st.sidebar.slider(
    "Binomial Steps",
    10, 300, 100
)


# ---------------------------------------------------
# Shared Market Data (Defined ONCE)
# ---------------------------------------------------
@st.cache_data
def load_market_data(ticker, expiry):
    S = get_spot_price(ticker)
    r = get_risk_free_rate()
    q = get_dividend_yield(ticker)
    chain = get_option_chain(ticker, expiry)
    return S, r, q, chain


S, r, q, chain = load_market_data(ticker, expiry)
T = time_to_expiry(expiry)
sigma_hist = calculate_historical_volatility(ticker, 30)

st.sidebar.write(f"Spot: {S:.2f}")
st.sidebar.write(f"Risk-Free Rate: {r:.4f}")
st.sidebar.write(f"Dividend Yield: {q:.4f}")
st.sidebar.write(f"Time to Expiry: {T:.4f} years")


# ===================================================
# PAGE 1 — MARKET OVERVIEW
# ===================================================
if page == "Market Overview":

    st.markdown("## 📊 Historical Price & Volume")
    st.divider()

    hist_period = st.selectbox(
        "Select Historical Period",
        ["6mo", "1y", "2y", "5y"],
        index=1
    )

    hist_data = get_historical_data(ticker, period=hist_period)

    fig_price = plot_price_volume_chart(hist_data, ticker)

    st.plotly_chart(fig_price, use_container_width=True)


# ===================================================
# PAGE 2 — OPTION PRICING
# ===================================================
if page == "Option Pricing":

    st.markdown("## 📈 Live Option Pricing")
    st.divider()

    bs_result = price_and_greeks(
        S, strike, T, r, sigma_hist, q, option_type
    )

    bin_price = binomial_option_price(
        S, strike, T, r, sigma_hist, q,
        steps=steps,
        option_type=option_type,
        american=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Black–Scholes (Historical Vol)")
        c1, c2, c3 = st.columns(3)
        c4, c5, c6 = st.columns(3)

        c1.metric("Price", f"{bs_result['price']:.2f}")
        c2.metric("Delta", f"{bs_result['delta']:.3f}")
        c3.metric("Gamma", f"{bs_result['gamma']:.4f}")
        c4.metric("Vega", f"{bs_result['vega']:.2f}")
        c5.metric("Theta", f"{bs_result['theta']:.2f}")
        c6.metric("Rho", f"{bs_result['rho']:.2f}")

    with col2:
        st.markdown("### Binomial (American)")
        st.metric("Price", f"{bin_price:.2f}")

    # Monte Carlo
    st.markdown("## 🎲 Monte Carlo Pricing")
    st.divider()

    simulations = st.slider(
        "Number of Simulations",
        1000, 200000, 50000, step=5000
    )

    mc_result = monte_carlo_option_price(
        S, strike, T, r, sigma_hist,
        option_type=option_type,
        simulations=simulations
    )

    colA, colB = st.columns(2)
    colA.metric("Monte Carlo Price", f"{mc_result['price']:.2f}")
    colB.metric(
        "95% CI",
        f"[{mc_result['ci_low']:.2f} , {mc_result['ci_high']:.2f}]"
    )

    # Early Exercise Premium
    euro_price = black_scholes_price(
        S, strike, T, r, sigma_hist, q, option_type
    )

    amer_price = binomial_option_price(
        S, strike, T, r, sigma_hist, q,
        steps=200,
        option_type=option_type,
        american=True
    )

    premium = amer_price - euro_price

    st.markdown("## 💰 Early Exercise Premium")
    st.metric("American − European", f"{premium:.4f}")


# ===================================================
# PAGE 3 — RISK & GREEKS
# ===================================================
if page == "Risk & Greeks":

    st.markdown("## 📊 Delta Curve")
    st.plotly_chart(
        plot_delta_curve(S, strike, T, r, sigma_hist, q, option_type),
        use_container_width=True
    )

    st.markdown("## 📈 Vega Curve")
    st.plotly_chart(
        plot_vega_curve(S, strike, T, r, q, option_type),
        use_container_width=True
    )

    st.markdown("## 🎛 Greeks Sensitivity")
    st.divider()

    s1, s2, s3 = st.columns(3)

    with s1:
        spot_slider = st.slider(
            "Spot",
            float(S * 0.7),
            float(S * 1.3),
            float(S)
        )

    with s2:
        vol_slider = st.slider(
            "Volatility",
            0.05, 1.0,
            float(sigma_hist)
        )

    with s3:
        time_slider = st.slider(
            "Time to Expiry",
            0.01, 1.0,
            float(T)
        )

    sens = price_and_greeks(
        spot_slider,
        strike,
        time_slider,
        r,
        vol_slider,
        q,
        option_type
    )

    g1, g2, g3 = st.columns(3)
    g4, g5, g6 = st.columns(3)

    g1.metric("Price", f"{sens['price']:.2f}")
    g2.metric("Delta", f"{sens['delta']:.3f}")
    g3.metric("Gamma", f"{sens['gamma']:.4f}")
    g4.metric("Vega", f"{sens['vega']:.2f}")
    g5.metric("Theta", f"{sens['theta']:.2f}")
    g6.metric("Rho", f"{sens['rho']:.2f}")

    # Binomial Tree Network
    st.markdown("## 🌳 Binomial Tree (Network)")
    tree_steps = st.slider("Tree Steps (visual)", 2, 6, 4)

    fig_tree = plot_binomial_tree_network(
        S, T, sigma_hist, tree_steps
    )

    st.plotly_chart(fig_tree, use_container_width=True)


# ===================================================
# PAGE 4 — VOLATILITY ANALYTICS
# ===================================================
if page == "Volatility Analytics":

    st.markdown("## Volatility Smile")
    st.divider()

    calls = chain[
        (chain["optionType"] == "call") &
        (chain["volume"] > 0)
    ].copy()

    calls["moneyness"] = calls["strike"] / S
    calls = calls[
        (calls["moneyness"] > 0.8) &
        (calls["moneyness"] < 1.2)
    ]

    calls = implied_volatility_chain(
        calls,
        S,
        T,
        r,
        q,
        option_type="call"
    )

    fig_smile = plot_volatility_smile(calls, ticker, expiry)
    st.plotly_chart(fig_smile, use_container_width=True)

    st.markdown("## Model Divergence")
    results = compare_models(
        calls, S, T, r, q,
        steps=steps,
        option_type="call"
    )

    st.write(results.head())
    st.write(results.columns)

    fig_div = plot_model_errors(results, ticker, expiry)
    st.plotly_chart(fig_div, use_container_width=True)

    # 3D Surface
    st.markdown("## 🌊 3D Volatility Surface")
    st.divider()

    expiries_list = get_expiry_dates(ticker)[:4]
    surface_rows = []

    for exp in expiries_list:

        T_temp = time_to_expiry(exp)
        chain_temp = get_option_chain(ticker, exp)

        calls_temp = chain_temp[
            (chain_temp["optionType"] == "call") &
            (chain_temp["volume"] > 0)
        ].copy()

        calls_temp["moneyness"] = calls_temp["strike"] / S
        calls_temp = calls_temp[
            (calls_temp["moneyness"] > 0.8) &
            (calls_temp["moneyness"] < 1.2)
        ]

        calls_temp = implied_volatility_chain(
            calls_temp,
            S,
            T_temp,
            r,
            q,
            option_type="call"
        )

        for _, row in calls_temp.iterrows():
            if not np.isnan(row["impliedVol"]):
                surface_rows.append({
                    "strike": row["strike"],
                    "T": T_temp,
                    "iv": row["impliedVol"]
                })

    surface_df = pd.DataFrame(surface_rows)

    if len(surface_df) > 0:

        pivot = surface_df.pivot_table(
            values="iv",
            index="T",
            columns="strike"
        )

        strikes = pivot.columns.values
        expiries_years = pivot.index.values
        iv_matrix = pivot.values

        fig_surface = plot_volatility_surface(
            strikes,
            expiries_years,
            iv_matrix,
            ticker
        )

        st.plotly_chart(fig_surface, use_container_width=True)

    else:
        st.warning("Not enough data to build surface.")