"""Black's (1976) model for interest rate derivatives."""
import numpy as np
from scipy.stats import norm

def black_formula(F: float, K: float, T: float, sigma: float, df: float, is_call: bool) -> float:
    """Core Black (1976) formula.
    
    Parameters
    ----------
    F : float
        Forward price / forward rate.
    K : float
        Strike.
    T : float
        Time to maturity.
    sigma : float
        Volatility.
    df : float
        Discount factor.
    is_call : bool
        True for call (e.g. caplet, payer swaption), False for put.
    """
    if T <= 0:
        if is_call:
            return df * max(F - K, 0.0)
        return df * max(K - F, 0.0)
        
    d1 = (np.log(F / K) + 0.5 * sigma**2 * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if is_call:
        return df * (F * norm.cdf(d1) - K * norm.cdf(d2))
    return df * (K * norm.cdf(-d2) - F * norm.cdf(-d1))
