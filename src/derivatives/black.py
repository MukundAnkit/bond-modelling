"""Black's (1976) model for interest rate derivatives."""

import numpy as np
from scipy.stats import norm


def black_formula(
    fwd: float, strike: float, t_exp: float, sigma: float, df: float, is_call: bool
) -> float:
    """Core Black (1976) formula.

    Parameters
    ----------
    fwd : float
        Forward price / forward rate.
    strike : float
        Strike.
    t_exp : float
        Time to maturity.
    sigma : float
        Volatility.
    df : float
        Discount factor.
    is_call : bool
        True for call (e.g. caplet, payer swaption), False for put.

    """
    if t_exp <= 0:
        if is_call:
            return df * max(fwd - strike, 0.0)
        return df * max(strike - fwd, 0.0)

    d1 = (np.log(fwd / strike) + 0.5 * sigma**2 * t_exp) / (sigma * np.sqrt(t_exp))
    d2 = d1 - sigma * np.sqrt(t_exp)

    if is_call:
        return float(df * (fwd * norm.cdf(d1) - strike * norm.cdf(d2)))
    return float(df * (strike * norm.cdf(-d2) - fwd * norm.cdf(-d1)))
