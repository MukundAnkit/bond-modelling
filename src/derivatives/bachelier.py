"""Bachelier (Normal) model for interest rate derivatives."""

from src.derivatives import aad


def bachelier_formula(
    fwd, strike, t_exp, vol, df, is_call: bool
):
    """Core Bachelier formula (Normal model).
    
    Parameters
    ----------
    fwd : float or Dual
        Forward price / rate.
    strike : float or Dual
        Strike price / rate.
    t_exp : float or Dual
        Time to maturity.
    vol : float or Dual
        Normal volatility (absolute volatility, e.g. 0.0050 for 50 bps).
    df : float or Dual
        Discount factor.
    is_call : bool
        True for call (e.g., caplet, payer swaption), False for put.
        
    Returns
    -------
    float or Dual
        The option price.

    """
    if float(t_exp) <= 0:
        if is_call:
            return df * aad.maximum(fwd - strike, 0.0)
        return df * aad.maximum(strike - fwd, 0.0)

    if float(vol) <= 0:
        if is_call:
            return df * aad.maximum(fwd - strike, 0.0)
        return df * aad.maximum(strike - fwd, 0.0)

    std_dev = vol * aad.sqrt(t_exp)
    d = (fwd - strike) / std_dev

    if is_call:
        return df * ((fwd - strike) * aad.norm_cdf(d) + std_dev * aad.norm_pdf(d))
    return df * ((strike - fwd) * aad.norm_cdf(-d) + std_dev * aad.norm_pdf(-d))
