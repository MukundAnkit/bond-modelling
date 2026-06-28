"""Convexity for fixed-rate bonds."""

import numpy as np

from src.instruments.bond import Bond
from src.instruments.pricing import price


def convexity(bond: Bond, yield_rate: float) -> float:
    """Calculate the convexity of a fixed-rate bond.

    Convexity measures the curvature of the price-yield relationship
    (second derivative of price with respect to yield, divided by price).

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    yield_rate : float
        Market yield (YTM) as a decimal.

    Returns
    -------
    float
        Convexity in years-squared.

    """
    p = price(bond, yield_rate)
    rate_per_period = yield_rate / bond.freq
    m = bond.freq
    t = np.arange(1, bond.periods + 1)
    cash_flows = np.full(bond.periods, bond.coupon_payment)
    cash_flows[-1] += bond.face_value
    weighted_pv = np.sum(
        t * (t + 1.0) / (m * m) * cash_flows / (1 + rate_per_period) ** (t + 2)
    )
    return float(weighted_pv / p)
