"""Log-linear discount-factor interpolation for bootstrapping."""

import numpy as np


def interpolate_df(
    t_target: float,
    known_maturities: np.ndarray,
    known_spot_rates: np.ndarray,
) -> float:
    """Interpolate (or forward-fill) a discount factor at an arbitrary time.

    Uses log-linear interpolation of discount factors between known points.
    For targets outside the grid, the nearest neighbour's discount factor
    is used (forward-fill).

    Parameters
    ----------
    t_target : float
        Target time in years.
    known_maturities : np.ndarray
        1-D array of known maturity points (years), strictly increasing.
    known_spot_rates : np.ndarray
        1-D array of zero-coupon spot rates (decimal) at each maturity.
        Same length as ``known_maturities``.

    Returns
    -------
    float
        Discount factor Z(t_target) = exp(-y(t_target) * t_target) via
        log-linear interpolation of the discount factors.

    """
    dfs = np.where(
        known_spot_rates == 0.0,
        1.0,
        1.0 / (1.0 + known_spot_rates) ** known_maturities,
    )

    if t_target <= known_maturities[0]:
        z = float(known_spot_rates[0])
        return float(1.0 / (1.0 + z) ** t_target)
    if t_target >= known_maturities[-1]:
        z = float(known_spot_rates[-1])
        return float(1.0 / (1.0 + z) ** t_target)

    log_dfs = np.log(dfs)
    t = float(t_target)
    idx = np.searchsorted(known_maturities, t, side="right") - 1
    t_left = float(known_maturities[idx])
    t_right = float(known_maturities[idx + 1])
    log_df_left = float(log_dfs[idx])
    log_df_right = float(log_dfs[idx + 1])
    weight = (t - t_left) / (t_right - t_left)
    log_df = log_df_left + weight * (log_df_right - log_df_left)
    return float(np.exp(log_df))
