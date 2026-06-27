"""Present-value pricing for fixed-rate bonds."""

import numpy as np

from src.instruments.bond import Bond


def price(bond: Bond, yield_rate: float) -> float:
    """Calculate the present value of all future bond cash flows.

    Parameters
    ----------
    bond : Bond
        The bond instrument to price.
    yield_rate : float
        Market yield (YTM) as a decimal.

    Returns
    -------
    float
        The bond's theoretical price (present value).

    """
    rate_per_period = yield_rate / bond.freq
    t = np.arange(1, bond.periods + 1)
    pv_coupons = np.sum(bond.coupon_payment / (1 + rate_per_period) ** t)
    pv_face = bond.face_value / (1 + rate_per_period) ** bond.periods
    return float(pv_coupons + pv_face)
