"""Prepayment models for Mortgage-Backed Securities."""

import numpy as np


def cpr_to_smm(cpr: float) -> float:
    """Convert CPR to Single Monthly Mortality (SMM)."""
    return float(1.0 - (1.0 - cpr) ** (1.0 / 12.0))


def smm_to_cpr(smm: float) -> float:
    """Convert SMM to Conditional Prepayment Rate (CPR)."""
    return float(1.0 - (1.0 - smm) ** 12.0)


def psa_to_cpr(psa: float, month: int) -> float:
    """Calculate CPR based on the PSA curve for a given month."""
    if month < 1:
        raise ValueError("Month must be >= 1")

    cpr_100 = min(month * 0.002, 0.06)
    return cpr_100 * (psa / 100.0)


def psa_to_smm(psa: float, month: int) -> float:
    """Calculate SMM based on the PSA curve for a given month."""
    cpr = psa_to_cpr(psa, month)
    return cpr_to_smm(cpr)


def richard_roll_cpr(
    wac: float,
    current_rate: float,
    t: int,
    month: int,
    pool_factor: float = 1.0,
    multiplier: float = 1.0,
) -> float:
    """Calculate CPR using a stylized Richard-Roll behavioral model.

    Factoring in refinancing incentives, burnout, seasonality, and aging.

    Args:
        wac: Weighted average coupon of the MBS pool.
        current_rate: Current market mortgage rate (for refinancing).
        t: Age of the MBS in months (1-indexed).
        month: Calendar month (1 to 12) for seasonality.
        pool_factor: Current pool factor (remaining balance / initial balance) for burnout.
        multiplier: Overall tuning multiplier.

    Returns:
        Conditional Prepayment Rate (CPR).

    """
    # 1. Refinancing Incentive (RI)
    rate_diff = (wac - current_rate) * 100  # in percentage points
    # Arctan function to model the S-curve of refinancing
    ri = 0.28 + 0.14 * np.arctan(-np.pi / 2 + 1.5 * rate_diff)
    ri = max(0.0, ri)

    # 2. Seasonality Multiplier (SM)
    seasonality = [
        0.94,
        0.76,
        0.74,
        0.95,
        0.98,
        0.92,
        0.98,
        1.10,
        1.18,
        1.22,
        1.23,
        0.98,
    ]
    sm = seasonality[(month - 1) % 12]

    # 3. Aging Multiplier (MM)
    mm = min(t / 30.0, 1.0) if t > 0 else 0.0

    # 4. Burnout Multiplier (BM)
    bm = 0.3 + 0.7 * pool_factor

    cpr = float(ri * sm * mm * bm * multiplier)
    return min(max(cpr, 0.0), 1.0)
