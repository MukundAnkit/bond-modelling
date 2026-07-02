# ruff: noqa
# mypy: ignore-errors
import numpy as np


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
    fca_spread: float,
    fba_spread: float,
    df: np.ndarray,
    dt: float,
) -> float:
    """
    Calculate Funding Valuation Adjustment (FVA), comprising FCA and FBA.

    Args:
        ee: Expected Exposure.
        ene: Expected Negative Exposure.
        fca_spread: Funding spread for borrowing.
        fba_spread: Funding spread for lending.
        df: Discount factor array.
        dt: Time step size.

    Returns:
        FVA value (FCA - FBA). FCA is a cost, FBA is a benefit.
    """
    fca = np.sum(fca_spread * ee * df * dt)
    fba = np.sum(fba_spread * np.abs(ene) * df * dt)
    return float(fca - fba)
