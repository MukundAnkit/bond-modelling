"""Value at Risk (VaR) and Expected Shortfall (ES) analytics."""

import numpy as np
from scipy.stats import norm, genpareto, skew, kurtosis
from scipy.integrate import quad

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.portfolio.portfolio import Portfolio
    from src.curve.nelson_siegel import NelsonSiegelCurve


def historical_var(pnl_vector: np.ndarray, confidence_level: float = 0.99) -> float:
    """Calculate Historical Value at Risk (VaR).

    Parameters
    ----------
    pnl_vector : np.ndarray
        Array of simulated or historical Portfolio P&L values.
    confidence_level : float, optional
        Confidence level for VaR (e.g., 0.99 for 99% VaR). Default is 0.99.

    Returns
    -------
    float
        The Value at Risk (expressed as a positive loss amount).

    """
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("Confidence level must be between 0 and 1.")

    percentile = (1.0 - confidence_level) * 100
    var = -np.percentile(pnl_vector, percentile)
    return float(max(0.0, var))


def historical_expected_shortfall(
    pnl_vector: np.ndarray, confidence_level: float = 0.99
) -> float:
    """Calculate Historical Expected Shortfall (Conditional VaR).

    Parameters
    ----------
    pnl_vector : np.ndarray
        Array of simulated or historical Portfolio P&L values.
    confidence_level : float, optional
        Confidence level (e.g., 0.99). Default is 0.99.

    Returns
    -------
    float
        The Expected Shortfall (expressed as a positive loss amount).

    """
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("Confidence level must be between 0 and 1.")

    var = historical_var(pnl_vector, confidence_level)
    # Filter PnL for values worse than or equal to -VaR
    tail_losses = pnl_vector[pnl_vector <= -var]

    if len(tail_losses) == 0:
        return var

    return float(-np.mean(tail_losses))


def full_revaluation_pnl(
    portfolio: 'Portfolio',
    base_curve: 'NelsonSiegelCurve',
    yield_shifts: np.ndarray,
) -> np.ndarray:
    """Calculate Full Revaluation P&L for a grid of yield curve shifts.

    Parameters
    ----------
    portfolio : Portfolio
        The portfolio to revalue.
    base_curve : NelsonSiegelCurve
        The current base yield curve.
    yield_shifts : np.ndarray
        A 1D array of parallel yield shifts (e.g., in absolute terms).

    Returns
    -------
    np.ndarray
        Array of P&L values.
    """
    base_val = portfolio.market_value(base_curve)
    pnl = np.zeros(len(yield_shifts))
    
    from src.curve.nelson_siegel import NelsonSiegelCurve
    
    for i, shift in enumerate(yield_shifts):
        # Apply a parallel shift by adjusting beta0
        shocked_curve = NelsonSiegelCurve(
            beta0=base_curve.beta0 + shift,
            beta1=base_curve.beta1,
            beta2=base_curve.beta2,
            tau=base_curve.tau
        )
        shocked_val = portfolio.market_value(shocked_curve)
        pnl[i] = shocked_val - base_val
        
    return pnl


def full_revaluation_var(
    portfolio: 'Portfolio',
    base_curve: 'NelsonSiegelCurve',
    yield_shifts: np.ndarray,
    confidence_level: float = 0.99,
) -> float:
    """Calculate Grid-based Full Revaluation Historical VaR.

    Parameters
    ----------
    portfolio : Portfolio
        The portfolio to revalue.
    base_curve : NelsonSiegelCurve
        The current base yield curve.
    yield_shifts : np.ndarray
        A 1D array of parallel yield shifts (e.g., in absolute terms).
    confidence_level : float, optional
        Confidence level (e.g., 0.99). Default is 0.99.

    Returns
    -------
    float
        The Full Revaluation Value at Risk.
    """
    pnl_vector = full_revaluation_pnl(portfolio, base_curve, yield_shifts)
    return historical_var(pnl_vector, confidence_level)


def cornish_fisher_var(
    pnl_vector: np.ndarray, confidence_level: float = 0.99
) -> float:
    """Calculate VaR using Cornish-Fisher expansion to capture skew and kurtosis.

    Parameters
    ----------
    pnl_vector : np.ndarray
        Array of simulated or historical Portfolio P&L values.
    confidence_level : float, optional
        Confidence level (e.g., 0.99). Default is 0.99.

    Returns
    -------
    float
        The Cornish-Fisher Value at Risk.
    """
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("Confidence level must be between 0 and 1.")
        
    alpha = 1.0 - confidence_level
    z = norm.ppf(alpha)
    
    s = skew(pnl_vector)
    k = kurtosis(pnl_vector)
    
    z_cf = z + (z**2 - 1) * s / 6.0 + (z**3 - 3*z) * k / 24.0 - (2*z**3 - 5*z) * (s**2) / 36.0
    
    mu = np.mean(pnl_vector)
    sigma = np.std(pnl_vector)
    
    var = -(mu + z_cf * sigma)
    return float(max(0.0, var))


def cornish_fisher_expected_shortfall(
    pnl_vector: np.ndarray, confidence_level: float = 0.99
) -> float:
    """Calculate Expected Shortfall using Cornish-Fisher expansion.

    Parameters
    ----------
    pnl_vector : np.ndarray
        Array of simulated or historical Portfolio P&L values.
    confidence_level : float, optional
        Confidence level (e.g., 0.99). Default is 0.99.

    Returns
    -------
    float
        The Cornish-Fisher Expected Shortfall.
    """
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("Confidence level must be between 0 and 1.")
        
    alpha = 1.0 - confidence_level
    
    def cf_quantile(p):
        z = norm.ppf(p)
        s = skew(pnl_vector)
        k = kurtosis(pnl_vector)
        z_cf = z + (z**2 - 1) * s / 6.0 + (z**3 - 3*z) * k / 24.0 - (2*z**3 - 5*z) * (s**2) / 36.0
        return z_cf
        
    mu = np.mean(pnl_vector)
    sigma = np.std(pnl_vector)
    
    # Numerical integration of the quantile function
    val, _ = quad(cf_quantile, 0.0, alpha)
    es = -(mu + sigma * (val / alpha))
    
    return float(max(0.0, es))


def pot_expected_shortfall(
    pnl_vector: np.ndarray, confidence_level: float = 0.99, threshold: float = None
) -> float:
    """Calculate Expected Shortfall using Peaks-Over-Threshold (POT) EVT.

    Parameters
    ----------
    pnl_vector : np.ndarray
        Array of simulated or historical Portfolio P&L values.
    confidence_level : float, optional
        Confidence level (e.g., 0.99). Default is 0.99.
    threshold : float, optional
        The loss threshold for EVT. If None, defaults to the 90th percentile of losses.

    Returns
    -------
    float
        The POT Expected Shortfall.
    """
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("Confidence level must be between 0 and 1.")
        
    losses = -pnl_vector
    
    if threshold is None:
        threshold = np.percentile(losses, 90)
        
    exceedances = losses[losses > threshold]
    if len(exceedances) < 5:
        # Not enough data in the tail, fallback
        return historical_expected_shortfall(pnl_vector, confidence_level)
        
    excesses = exceedances - threshold
    c, loc, scale = genpareto.fit(excesses, floc=0)
    
    n_u = len(exceedances)
    n = len(losses)
    p_u = n_u / n
    
    alpha = 1.0 - confidence_level
    if alpha >= p_u:
        return historical_expected_shortfall(pnl_vector, confidence_level)
    
    var = threshold + (scale / c) * (((alpha / p_u)**(-c)) - 1)
    es = (var + scale - c * threshold) / (1 - c)
    
    return float(max(0.0, es))
