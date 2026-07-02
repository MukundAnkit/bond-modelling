"""Reduced-Form Credit Models."""

from collections.abc import Callable

import numpy as np


def constant_hazard_survival(lam: float, t: float) -> float:
    """Calculate survival probability under a constant hazard rate.

    Parameters
    ----------
    lam : float
        Constant hazard rate (default intensity).
    t : float
        Time horizon in years.

    Returns
    -------
    float
        Survival probability S(t).

    """
    return float(np.exp(-lam * t))


def piecewise_hazard_survival(
    hazard_rates: list[float], times: list[float], t: float
) -> float:
    """Calculate survival probability under a piecewise constant hazard rate curve.

    Parameters
    ----------
    hazard_rates : List[float]
        List of hazard rates for each interval.
    times : List[float]
        List of interval end times (must be strictly increasing).
    t : float
        Target time horizon in years.

    Returns
    -------
    float
        Survival probability S(t).

    """
    if len(hazard_rates) != len(times):
        raise ValueError("Lengths of hazard_rates and times must match.")

    integral = 0.0
    prev_time = 0.0

    for h, time_end in zip(hazard_rates, times, strict=True):
        if t <= prev_time:
            break

        dt = min(t, time_end) - prev_time
        integral += h * dt
        prev_time = time_end

        if t <= time_end:
            break

    if t > prev_time:
        integral += hazard_rates[-1] * (t - prev_time)

    return float(np.exp(-integral))


def calibrate_hazard_rates(
    maturities: np.ndarray, spreads: np.ndarray, recovery_rate: float
) -> np.ndarray:
    """Bootstrap piecewise constant hazard rates from bond spreads.

    Parameters
    ----------
    maturities : np.ndarray
        Bond maturities in years.
    spreads : np.ndarray
        Credit spreads for each maturity (continuous).
    recovery_rate : float
        Expected recovery rate.

    Returns
    -------
    np.ndarray
        Piecewise constant hazard rates for each maturity interval.

    """
    survival: list[float] = []
    hazard_rates_list: list[float] = []

    for i, (t, s) in enumerate(zip(maturities, spreads, strict=True)):
        surv = (np.exp(-s * t) - recovery_rate) / (1.0 - recovery_rate)
        surv = max(surv, 1e-10)
        survival.append(float(surv))

        cum_hazard = -np.log(survival[i])
        prev_hazard = 0.0 if i == 0 else -np.log(survival[i - 1])
        dt = t if i == 0 else t - maturities[i - 1]
        lam = (cum_hazard - prev_hazard) / dt
        hazard_rates_list.append(float(max(lam, 0.0)))

    return np.array(hazard_rates_list)


def jarrow_turnbull_price(
    curve: Callable[[float], float],
    survival: Callable[[float], float],
    recovery_rate: float,
    t_mat: float,
) -> float:
    """Calculate price of a zero-coupon defaultable bond (Jarrow-Turnbull simplified).

    Assumes Recovery of Face Value (RFV) paid at maturity.

    Parameters
    ----------
    curve : callable
        Continuous risk-free yield curve.
    survival : callable
        Continuous survival probability curve S(t).
    recovery_rate : float
        Expected recovery rate.
    t_mat : float
        Maturity of the zero-coupon bond.

    Returns
    -------
    float
        The present value (price as percentage of par) of the defaultable bond.

    """
    r = curve(t_mat)
    df = np.exp(-r * t_mat)
    s = survival(t_mat)

    expected_payoff = recovery_rate + (1.0 - recovery_rate) * s

    return float(df * expected_payoff)
