"""Bootstrapping algorithm for extracting zero-coupon spot rates."""

import numpy as np

from src.bootstrap.interpolate import interpolate_df


def bootstrap_spot_rates(
    maturities: np.ndarray,
    par_yields: np.ndarray,
    freq: int = 1,
) -> np.ndarray:
    """Extract zero-coupon spot rates from par yields via bootstrapping.

    Implements the recursive strip algorithm: the first spot rate equals the
    first par yield; each subsequent spot rate is solved by discounting all
    earlier coupons at previously computed spot rates.

    Parameters
    ----------
    maturities : np.ndarray
        1-D array of maturities in years, strictly increasing (e.g. [1, 2, 3]).
    par_yields : np.ndarray
        1-D array of par yields as decimals, same length as maturities.
    freq : int, optional
        Coupon payments per year. ``1`` (annual) or ``2`` (semi-annual).
        Default is ``1``.

    Returns
    -------
    np.ndarray
        Zero-coupon spot rates at each maturity, same length as inputs.

    Raises
    ------
    ValueError
        If inputs fail validation (non-increasing maturities, length mismatch,
        invalid freq, or maturities < 0.5 for semi-annual).

    """
    if len(maturities) != len(par_yields):
        raise ValueError("maturities and par_yields must have the same length")
    if freq not in (1, 2):
        raise ValueError("freq must be 1 (annual) or 2 (semi-annual)")
    if len(maturities) == 0:
        return np.array([], dtype=np.float64)
    if np.any(maturities <= 0):
        raise ValueError("maturities must be positive")
    if np.any(np.diff(maturities) <= 0):
        raise ValueError("maturities must be strictly increasing")
    if freq == 2 and maturities[0] < 0.5:
        raise ValueError("First maturity must be >= 0.5 for semi-annual bootstrapping")

    n = len(maturities)
    spot_rates = np.empty(n, dtype=np.float64)
    face_value = 100.0

    for i in range(n):
        t_i = maturities[i]
        c_i = par_yields[i]
        coupon = face_value * c_i / freq

        if i == 0:
            spot_rates[i] = c_i
            continue

        known_mats = maturities[:i]
        known_spots = spot_rates[:i]
        n_periods = int(round(t_i * freq))
        pv_known = 0.0

        for k in range(1, n_periods + 1):
            t_k = k / freq
            if abs(t_k - t_i) < 1e-12:
                continue
            df = interpolate_df(t_k, known_mats, known_spots)
            pv_known += coupon * df

        remaining = face_value - pv_known
        final_cf = coupon + face_value
        spot_rates[i] = (final_cf / remaining) ** (1.0 / t_i) - 1.0

    return spot_rates
