import numpy as np

def monte_carlo_option_price(
    S, K, T, r, sigma,
    option_type="call",
    simulations=100000,
    antithetic=True
):

    if antithetic:
        Z = np.random.randn(simulations // 2)
        Z = np.concatenate([Z, -Z])
    else:
        Z = np.random.randn(simulations)

    ST = S * np.exp(
        (r - 0.5 * sigma**2) * T +
        sigma * np.sqrt(T) * Z
    )

    if option_type == "call":
        payoffs = np.maximum(ST - K, 0)
    else:
        payoffs = np.maximum(K - ST, 0)

    discounted = np.exp(-r * T) * payoffs

    price = np.mean(discounted)
    std_error = np.std(discounted) / np.sqrt(len(discounted))

    return {
        "price": price,
        "std_error": std_error,
        "ci_low": price - 1.96 * std_error,
        "ci_high": price + 1.96 * std_error
    }