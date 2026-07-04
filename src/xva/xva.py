# ruff: noqa
# mypy: ignore-errors
import numpy as np
from typing import Union
from scipy.stats import norm, rankdata


def calculate_cva(ee: np.ndarray, pd: np.ndarray, lgd: float, df: np.ndarray) -> float:
    """
    Calculate Credit Valuation Adjustment (CVA).

    Args:
        ee: Expected Exposure array over time.
        pd: Marginal Probability of Default array of the counterparty over time.
        lgd: Loss Given Default of the counterparty.
        df: Discount factor array over time.

    Returns:
        CVA value.
    """
    return float(np.sum(lgd * ee * pd * df))


def calculate_dva(
    ene: np.ndarray, pd_own: np.ndarray, lgd_own: float, df: np.ndarray
) -> float:
    """
    Calculate Debt Valuation Adjustment (DVA).

    Args:
        ene: Expected Negative Exposure array over time. (values are <= 0)
        pd_own: Marginal Probability of Default array of the firm itself over time.
        lgd_own: Loss Given Default of the firm itself.
        df: Discount factor array over time.

    Returns:
        DVA value (usually reported as a positive number or subtracted from CVA, here we return absolute impact).
        Note: ENE is negative, so DVA will be calculated as a positive benefit.
    """
    # DVA is a benefit, so it is positive in value adjustments. ENE is negative.
    return float(np.sum(lgd_own * np.abs(ene) * pd_own * df))


def calculate_fva(
    ee: np.ndarray,
    ene: np.ndarray,
    fca_spread: Union[float, np.ndarray],
    fba_spread: Union[float, np.ndarray],
    df: np.ndarray,
    dt: float,
) -> float:
    """
    Calculate Funding Valuation Adjustment (FVA), comprising FCA and FBA.

    Args:
        ee: Expected Exposure.
        ene: Expected Negative Exposure.
        fca_spread: Funding spread for borrowing (scalar or array).
        fba_spread: Funding spread for lending (scalar or array).
        df: Discount factor array.
        dt: Time step size.

    Returns:
        FVA value (FCA - FBA). FCA is a cost, FBA is a benefit.
    """
    fca = np.sum(fca_spread * ee * df * dt)
    fba = np.sum(fba_spread * np.abs(ene) * df * dt)
    return float(fca - fba)


def calculate_cva_wwr(
    exposure_paths: np.ndarray,
    pd_marginal: np.ndarray,
    lgd: float,
    df: np.ndarray,
    correlation: float,
) -> float:
    """
    Calculate Credit Valuation Adjustment (CVA) with Wrong-Way Risk (WWR) using a Gaussian copula.

    Args:
        exposure_paths: 2D array (num_paths, num_time_steps) of positive exposures.
        pd_marginal: 1D array of marginal probability of default in each time step.
        lgd: Loss Given Default.
        df: 1D array of discount factors.
        correlation: Correlation between exposure and default. Positive correlation means WWR.

    Returns:
        CVA value incorporating WWR.
    """
    num_paths, num_time_steps = exposure_paths.shape
    cva_paths = np.zeros(num_paths)

    for t in range(num_time_steps):
        ranks = rankdata(exposure_paths[:, t])
        u = ranks / (num_paths + 1)
        z_e = norm.ppf(u)

        if correlation == 0.0:
            pd_cond = np.full(num_paths, pd_marginal[t])
        else:
            z_pd = norm.ppf(pd_marginal[t])
            # Positive correlation -> higher exposure mapped to higher z_e -> higher pd_cond
            pd_cond = norm.cdf((z_pd + correlation * z_e) / np.sqrt(1 - correlation**2))

        cva_paths += lgd * exposure_paths[:, t] * pd_cond * df[t]

    return float(np.mean(cva_paths))


def calculate_kva(
    capital_paths: Union[float, np.ndarray],
    cost_of_capital: float,
    df: np.ndarray,
    dt: float,
) -> float:
    """
    Calculate Capital Valuation Adjustment (KVA).

    Args:
        capital_paths: 1D array of expected regulatory capital over time,
                       or 2D array of simulated capital paths.
        cost_of_capital: The hurdle rate or cost of capital (e.g., 0.10 for 10%).
        df: Discount factor array over time.
        dt: Time step size.

    Returns:
        KVA value.
    """
    if isinstance(capital_paths, np.ndarray) and capital_paths.ndim == 2:
        expected_capital = np.mean(capital_paths, axis=0)
    else:
        expected_capital = capital_paths

    return float(np.sum(cost_of_capital * expected_capital * df * dt))
