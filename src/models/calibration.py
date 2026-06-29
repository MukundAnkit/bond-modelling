import numpy as np  # noqa: D100


def calibrate_vasicek(
    rates: np.ndarray, dt: float = 1 / 252
) -> tuple[float, float, float]:
    """Calibrate Vasicek model parameters using Ordinary Least Squares.

    Args:
        rates: Time-series of short rates (e.g., daily 1-month or 3-month Treasury yields).
        dt: Time step in years (default 1/252 for daily data).

    Returns:
        (a, b, sigma) parameters.
    """  # noqa: D413, E501
    x = rates[:-1]
    y = rates[1:]

    # Linear regression: y = beta_0 + beta_1 * x
    A = np.vstack([np.ones(len(x)), x]).T  # noqa: N806
    beta_0, beta_1 = np.linalg.lstsq(A, y, rcond=None)[0]

    a = (1.0 - beta_1) / dt
    b = beta_0 / (a * dt)

    residuals = y - (beta_0 + beta_1 * x)
    sigma = np.std(residuals) / np.sqrt(dt)

    return a, b, sigma


def calibrate_cir(rates: np.ndarray, dt: float = 1 / 252) -> tuple[float, float, float]:
    """Calibrate CIR model parameters using Ordinary Least Squares.

    Args:
        rates: Time-series of short rates (strictly positive).
        dt: Time step in years (default 1/252 for daily data).

    Returns:
        (a, b, sigma) parameters.
    """  # noqa: D413
    # Prevent divide by zero if rates hit 0 exactly
    eps = 1e-8
    r = np.maximum(rates, eps)

    x = r[:-1]
    y = r[1:]

    dy = y - x

    # CIR discretization: dy / sqrt(x) = (a*b / sqrt(x)) * dt - a * sqrt(x) * dt + sigma * dW  # noqa: E501
    # Y = dy / sqrt(x)
    # X1 = 1 / sqrt(x)
    # X2 = sqrt(x)
    # Y = beta_1 * X1 + beta_2 * X2

    Y = dy / np.sqrt(x)  # noqa: N806
    X1 = 1.0 / np.sqrt(x)  # noqa: N806
    X2 = np.sqrt(x)  # noqa: N806

    A = np.vstack([X1, X2]).T  # noqa: N806
    beta_1, beta_2 = np.linalg.lstsq(A, Y, rcond=None)[0]

    a = -beta_2 / dt
    b = beta_1 / (a * dt)

    residuals = Y - (beta_1 * X1 + beta_2 * X2)
    sigma = np.std(residuals) / np.sqrt(dt)

    return a, b, sigma
