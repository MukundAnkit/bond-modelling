"""Cash flow generation utilities."""

import numpy as np

from src.instruments.bond import Bond


def generate_cashflows(bond: Bond) -> tuple[np.ndarray, np.ndarray]:
    """Generate the times and amounts of all cash flows for a bond.

    Parameters
    ----------
    bond : Bond
        The bond instrument.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        A tuple of (times_in_periods, cash_flow_amounts).
        - times_in_periods: 1D array of integers [1, 2, ..., n]
        - cash_flow_amounts: 1D array of dollar amounts for each period.

    """
    t = np.arange(1, bond.periods + 1)
    cf = np.full(bond.periods, bond.coupon_payment)
    cf[-1] += bond.face_value
    return t, cf
