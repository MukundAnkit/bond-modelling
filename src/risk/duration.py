"""Macaulay Duration and Modified Duration for fixed-rate bonds."""

import numpy as np

from src.instruments.bond import Bond
from src.instruments.pricing import price


def macaulay_duration(bond: Bond, yield_rate: float) -> float:
    """Calculate the Macaulay Duration of a fixed-rate bond.

    The Macaulay Duration is the weighted-average time to receive each
    cash flow, measured in years.

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    yield_rate : float
        Market yield (YTM) as a decimal.

    Returns
    -------
    float
        Macaulay Duration in years.

    """
    p = price(bond, yield_rate)
    rate_per_period = yield_rate / bond.freq
    t = np.arange(1, bond.periods + 1)
    cash_flows = np.full(bond.periods, bond.coupon_payment)
    cash_flows[-1] += bond.face_value
    weighted_pv = np.sum((t / bond.freq) * cash_flows / (1 + rate_per_period) ** t)
    return float(weighted_pv / p)


def modified_duration(bond: Bond, yield_rate: float) -> float:
    """Calculate the Modified Duration of a fixed-rate bond.

    Modified Duration approximates the percentage price sensitivity to
    a change in yield: ModD = MacD / (1 + y/m).

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    yield_rate : float
        Market yield (YTM) as a decimal.

    Returns
    -------
    float
        Modified Duration in years.

    """
    macd = macaulay_duration(bond, yield_rate)
    return macd / (1 + yield_rate / bond.freq)
