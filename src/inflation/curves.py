"""Real yield curves and breakeven inflation calculations."""

import numpy as np

from src.bootstrap.bootstrap import bootstrap_spot_rates


def bootstrap_real_rates(
    maturities: np.ndarray, real_par_yields: np.ndarray, freq: int = 2
) -> np.ndarray:
    """Bootstrap real spot rates from TIPS par yields.

    Since TIPS cash flows are fixed in real terms, the exact same
    bootstrapping algorithm for nominal bonds applies to real rates.

    Parameters
    ----------
    maturities : np.ndarray
        Maturities in years.
    real_par_yields : np.ndarray
        Real par yields from TIPS.
    freq : int, optional
        Coupon frequency. Default is 2 (semi-annual).

    Returns
    -------
    np.ndarray
        Real zero-coupon spot rates.

    """
    return bootstrap_spot_rates(maturities, real_par_yields, freq)


def breakeven_inflation(
    nominal_spots: np.ndarray, real_spots: np.ndarray
) -> np.ndarray:
    """Calculate breakeven inflation rates from nominal and real spot curves.

    Parameters
    ----------
    nominal_spots : np.ndarray
        Nominal zero-coupon spot rates.
    real_spots : np.ndarray
        Real zero-coupon spot rates.

    Returns
    -------
    np.ndarray
        Market-implied breakeven inflation rates.

    """
    if len(nominal_spots) != len(real_spots):
        raise ValueError("nominal and real curves must have the same length")
    if len(nominal_spots) == 0:
        return np.array([], dtype=np.float64)

    return (1.0 + nominal_spots) / (1.0 + real_spots) - 1.0
