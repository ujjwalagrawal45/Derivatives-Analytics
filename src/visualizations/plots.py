import plotly.graph_objects as go
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ----------------------------
# 3D Volatility Surface
# ----------------------------
def plot_volatility_surface(strikes, expiries, iv_matrix, ticker):

    fig = go.Figure(
        data=[
            go.Surface(
                x=strikes,
                y=expiries,
                z=iv_matrix
            )
        ]
    )

    fig.update_layout(
        title=f"{ticker} Implied Volatility Surface",
        scene=dict(
            xaxis_title="Strike",
            yaxis_title="Time to Expiry (Years)",
            zaxis_title="Implied Volatility"
        ),
        template="plotly_dark",
        height=700
    )

    return fig

# ----------------------------
# Volatility Smile Panel
# ----------------------------
def plot_volatility_smile(options_df, ticker, expiry):

    df = options_df.dropna(subset=["impliedVol"])

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["strike"],
            y=df["impliedVol"],
            mode="lines+markers"
        )
    )

    fig.update_layout(
        title=f"{ticker} Volatility Smile ({expiry})",
        xaxis_title="Strike Price",
        yaxis_title="Implied Volatility",
        template="plotly_dark"
    )

    return fig

# ----------------------------
# Binomial Tree Network
# ----------------------------
def plot_binomial_tree_network(S, T, sigma, steps):

    import numpy as np

    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u

    nodes_x = []
    nodes_y = []
    labels = []

    edges_x = []
    edges_y = []

    # Generate node positions
    for step in range(steps + 1):
        for i in range(step + 1):

            price = S * (u ** (step - i)) * (d ** i)

            x = step
            y = price

            nodes_x.append(x)
            nodes_y.append(y)
            labels.append(f"{price:.2f}")

            # Add edges to next step
            if step < steps:
                up_price = S * (u ** (step + 1 - i)) * (d ** i)
                down_price = S * (u ** (step - i)) * (d ** (i + 1))

                # Up move edge
                edges_x += [x, step + 1, None]
                edges_y += [price, up_price, None]

                # Down move edge
                edges_x += [x, step + 1, None]
                edges_y += [price, down_price, None]

    fig = go.Figure()

    # Edges
    fig.add_trace(
        go.Scatter(
            x=edges_x,
            y=edges_y,
            mode="lines",
            line=dict(width=1),
            hoverinfo="none"
        )
    )

    # Nodes
    fig.add_trace(
        go.Scatter(
            x=nodes_x,
            y=nodes_y,
            mode="markers+text",
            text=labels,
            textposition="top center",
            marker=dict(size=10),
            hoverinfo="text"
        )
    )

    fig.update_layout(
        title="Binomial Stock Price Tree",
        showlegend=False,
        template="plotly_dark",
        xaxis_title="Time Step",
        yaxis_title="Stock Price"
    )

    return fig

def plot_delta_curve(S, K, T, r, sigma, q, option_type):

    import numpy as np
    from src.models.black_scholes import price_and_greeks
    import plotly.graph_objects as go

    spot_range = np.linspace(S*0.7, S*1.3, 50)

    deltas = []

    for s in spot_range:
        greeks = price_and_greeks(
            s, K, T, r, sigma, q, option_type
        )
        deltas.append(greeks["delta"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=spot_range,
        y=deltas,
        mode="lines"
    ))

    fig.update_layout(
        title="Delta vs Spot",
        xaxis_title="Spot Price",
        yaxis_title="Delta",
        template="plotly_dark"
    )

    return fig

def plot_vega_curve(S, K, T, r, q, option_type):

    import numpy as np
    from src.models.black_scholes import price_and_greeks
    import plotly.graph_objects as go

    vol_range = np.linspace(0.05, 1.0, 50)
    vegas = []

    for vol in vol_range:
        greeks = price_and_greeks(
            S, K, T, r, vol, q, option_type
        )
        vegas.append(greeks["vega"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=vol_range,
        y=vegas,
        mode="lines"
    ))

    fig.update_layout(
        title="Vega vs Volatility",
        xaxis_title="Volatility",
        yaxis_title="Vega",
        template="plotly_dark"
    )

    return fig

# -----------------------------------
# Historic Price + Volume plot
# -----------------------------------
def plot_price_volume_chart(hist_df, ticker):

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3]
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=hist_df.index,
            open=hist_df["Open"],
            high=hist_df["High"],
            low=hist_df["Low"],
            close=hist_df["Close"],
            name="Price"
        ),
        row=1,
        col=1
    )

    # Volume
    fig.add_trace(
        go.Bar(
            x=hist_df.index,
            y=hist_df["Volume"],
            name="Volume"
        ),
        row=2,
        col=1
    )

    fig.update_layout(
        title=f"{ticker} Historical Price & Volume",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        showlegend=False
    )

    return fig

# -------------------------------
# Plot Model Errors
# -------------------------------
def plot_model_errors(results_df, ticker, expiry):

    if results_df.empty:
        return None

    fig = go.Figure()

    # Black-Scholes Error
    fig.add_trace(
        go.Scatter(
            x=results_df["strike"],
            y=results_df["bs_error"],
            mode="lines+markers",
            name="Market − Black-Scholes"
        )
    )

    # Binomial Error
    fig.add_trace(
        go.Scatter(
            x=results_df["strike"],
            y=results_df["binomial_error"],
            mode="lines+markers",
            name="Market − Binomial"
        )
    )

    fig.add_hline(y=0, line_dash="dash")

    fig.update_layout(
        title=f"{ticker} Model Pricing Errors ({expiry})",
        xaxis_title="Strike",
        yaxis_title="Pricing Error",
        template="plotly_dark"
    )

    return fig