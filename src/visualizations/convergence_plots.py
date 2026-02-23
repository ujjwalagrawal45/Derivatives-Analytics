def plot_model_errors(results, ticker, expiry):

    import plotly.graph_objects as go

    strikes = [r["strike"] for r in results]
    bs_err = [r["bs_error"] for r in results]
    bin_err = [r["binomial_error"] for r in results]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=strikes,
            y=bs_err,
            mode="lines+markers",
            name="Black-Scholes Error"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=strikes,
            y=bin_err,
            mode="lines+markers",
            name="Binomial Error"
        )
    )

    fig.update_layout(
        title=f"{ticker} Model Pricing Error ({expiry})",
        xaxis_title="Strike",
        yaxis_title="Model Price − Market Price",
        template="plotly_dark"
    )

    return fig