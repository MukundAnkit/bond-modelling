"""SABR model implementation for implied volatilities."""

import numpy as np

from src.derivatives import aad


def sabr_normal_vol(
    fwd: float | aad.Dual,
    strike: float | aad.Dual,
    t_exp: float | aad.Dual,
    alpha: float | aad.Dual,
    rho: float | aad.Dual,
    nu: float | aad.Dual,
) -> float | aad.Dual:
    """Calculate the Normal (Bachelier) implied volatility using the SABR model (beta=0).

    The beta=0 SABR model is well-suited for normal/Bachelier implied volatilities,
    which can handle negative forward rates and strikes gracefully.

    Parameters
    ----------
    fwd : float or Dual
        Forward rate.
    strike : float or Dual
        Strike rate.
    t_exp : float or Dual
        Time to expiry.
    alpha : float or Dual
        Initial volatility parameter.
    rho : float or Dual
        Correlation between forward and volatility (-1 <= rho <= 1).
    nu : float or Dual
        Volatility of volatility (nu > 0).

    Returns
    -------
    float or Dual
        The Normal (Bachelier) implied volatility.

    """
    if float(t_exp) <= 0.0:
        return alpha

    if np.isclose(float(fwd), float(strike)):
        # ATM limit where zeta -> 0
        vol = alpha * (1.0 + ((2.0 - 3.0 * rho**2) / 24.0 * nu**2) * t_exp)
        return vol

    zeta = (nu / alpha) * (fwd - strike)

    # x(zeta) = ln( (sqrt(1 - 2*rho*zeta + zeta^2) + zeta - rho) / (1 - rho) )
    sqrt_term = aad.sqrt(1.0 - 2.0 * rho * zeta + zeta**2)
    numerator = sqrt_term + zeta - rho
    denominator = 1.0 - rho

    # Handle numerical issues when rho -> 1
    if np.isclose(float(denominator), 0.0):
        denominator = 1e-10

    x_zeta = aad.log(numerator / denominator)

    if np.isclose(float(x_zeta), 0.0):
        # Fallback to ATM if x_zeta is effectively zero
        factor: float | aad.Dual = 1.0
    else:
        factor = zeta / x_zeta

    vol = alpha * factor * (1.0 + ((2.0 - 3.0 * rho**2) / 24.0 * nu**2) * t_exp)
    return vol
