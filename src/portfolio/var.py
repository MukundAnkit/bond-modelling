"""Value at Risk (VaR) and Expected Shortfall (ES) analytics."""

import numpy as np
from scipy.stats import norm


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


def parametric_var(
    portfolio_value: float,
    duration: float,
    yield_volatility: float,
    confidence_level: float = 0.99,
) -> float:
    """Calculate Parametric (Variance-Covariance) Value at Risk for a bond portfolio.

    Uses the delta-normal approach mapping yield volatility to price volatility
    via Modified Duration.

    Parameters
    ----------
    portfolio_value : float
        Current market value of the portfolio.
    duration : float
        Modified duration of the portfolio.
    yield_volatility : float
        Standard deviation of yield changes (absolute terms, e.g., 0.01 for 100 bps).
    confidence_level : float, optional
        Confidence level (e.g., 0.99). Default is 0.99.

    Returns
    -------
    float
        The Parametric Value at Risk (positive loss amount).

    """
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("Confidence level must be between 0 and 1.")

    z_score = norm.ppf(confidence_level)
    # Price Volatility = Duration * Yield Volatility
    price_volatility = duration * yield_volatility
    return float(portfolio_value * price_volatility * z_score)


def parametric_expected_shortfall(
    portfolio_value: float,
    duration: float,
    yield_volatility: float,
    confidence_level: float = 0.99,
) -> float:
    """Calculate Parametric Expected Shortfall for a bond portfolio.

    Parameters
    ----------
    portfolio_value : float
        Current market value of the portfolio.
    duration : float
        Modified duration of the portfolio.
    yield_volatility : float
        Standard deviation of yield changes.
    confidence_level : float, optional
        Confidence level (e.g., 0.99). Default is 0.99.

    Returns
    -------
    float
        The Parametric Expected Shortfall (positive loss amount).

    """
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("Confidence level must be between 0 and 1.")

    price_volatility = duration * yield_volatility
    std_dev_pnl = portfolio_value * price_volatility

    # Formula for ES of a normal distribution
    alpha = 1.0 - confidence_level
    z_score = norm.ppf(confidence_level)
    pdf_val = norm.pdf(z_score)

    es = std_dev_pnl * (pdf_val / alpha)
    return float(es)
