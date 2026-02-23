import numpy as np


# ----------------------------
# Core CRR Binomial Model
# ----------------------------
def binomial_option_price(
    S,
    K,
    T,
    r,
    sigma,
    q=0.0,
    steps=100,
    option_type="call",
    american=True
):

    if steps <= 0:
        raise ValueError("steps must be positive")

    dt = T / steps

    # CRR parameters
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u

    disc = np.exp(-r * dt)

    p = (
        np.exp((r - q) * dt) - d
    ) / (u - d)

    if not (0 <= p <= 1):
        raise ValueError("Invalid risk-neutral probability")


    # ----------------------------
    # Terminal stock prices
    # ----------------------------
    stock_prices = np.zeros(steps + 1)

    for i in range(steps + 1):
        stock_prices[i] = (
            S
            * (u ** (steps - i))
            * (d ** i)
        )


    # ----------------------------
    # Terminal option values
    # ----------------------------
    option_values = np.zeros(steps + 1)

    if option_type.lower() == "call":

        option_values = np.maximum(
            stock_prices - K,
            0
        )

    elif option_type.lower() == "put":

        option_values = np.maximum(
            K - stock_prices,
            0
        )

    else:
        raise ValueError("option_type must be call or put")


    # ----------------------------
    # Backward induction
    # ----------------------------
    for step in range(steps - 1, -1, -1):

        for i in range(step + 1):

            continuation = (
                p * option_values[i]
                + (1 - p) * option_values[i + 1]
            ) * disc

            if american:

                stock_price = (
                    S
                    * (u ** (step - i))
                    * (d ** i)
                )

                if option_type.lower() == "call":

                    exercise = max(
                        stock_price - K,
                        0
                    )

                else:

                    exercise = max(
                        K - stock_price,
                        0
                    )

                option_values[i] = max(
                    continuation,
                    exercise
                )

            else:

                option_values[i] = continuation


    return float(option_values[0])


# ----------------------------
# Tree generator for visualization
# ----------------------------
def generate_stock_tree(
    S,
    T,
    sigma,
    steps
):

    dt = T / steps

    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u

    tree = []

    for step in range(steps + 1):

        level = []

        for i in range(step + 1):

            price = (
                S
                * (u ** (step - i))
                * (d ** i)
            )

            level.append(price)

        tree.append(level)

    return tree