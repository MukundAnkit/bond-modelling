"""Present-value pricing for fixed-rate bonds."""

import numpy as np

from src.instruments.bond import Bond
from src.utils.cashflows import generate_cashflows


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
    t, cf = generate_cashflows(bond)

    # Calculate present value
    pv = np.sum(cf / (1 + rate_per_period) ** t)
    return float(pv)
