"""Credit Default Swap (CDS) pricing module."""

import datetime
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from scipy.optimize import root_scalar


@dataclass
class CDS:
    """Credit Default Swap.

    Parameters
    ----------
    notional : float
        The notional amount protected.
    spread : float
        The CDS premium spread (annualized).
    tenor : float
        The maturity of the CDS in years.
    freq : int
        Payment frequency (e.g., 4 for quarterly).

    """

    notional: float
    spread: float
    tenor: float
    freq: int

    def __post_init__(self) -> None:  # noqa: D105
        if self.notional <= 0:
            raise ValueError("Notional must be positive.")
        if self.tenor <= 0:
            raise ValueError("Tenor must be strictly positive.")
        if self.freq not in [1, 2, 4, 12]:
            raise ValueError("Frequency must be 1, 2, 4, or 12.")


def cds_premium_leg(
    cds: CDS, curve: Callable[[float], float], survival_curve: Callable[[float], float]
) -> float:
    """Calculate the Present Value (PV) of the CDS premium leg.

    Parameters
    ----------
    cds : CDS
        The Credit Default Swap instrument.
    curve : callable
        Continuous risk-free yield curve.
    survival_curve : callable
        Continuous survival probability curve S(t).

    Returns
    -------
    float
        The PV of the premium leg.

    """
    dt = 1.0 / cds.freq
    periods = int(cds.tenor * cds.freq)

    pv = 0.0
    for i in range(1, periods + 1):
        t = i * dt
        r = curve(t)
        df = np.exp(-r * t)
        s = survival_curve(t)

        pv += cds.spread * dt * df * s

    return float(pv * cds.notional)


def cds_protection_leg(
    cds: CDS,
    curve: Callable[[float], float],
    survival_curve: Callable[[float], float],
    recovery_rate: float,
) -> float:
    """Calculate the Present Value (PV) of the CDS protection leg.

    Parameters
    ----------
    cds : CDS
        The Credit Default Swap instrument.
    curve : callable
        Continuous risk-free yield curve.
    survival_curve : callable
        Continuous survival probability curve S(t).
    recovery_rate : float
        The expected recovery rate on the underlying reference asset.

    Returns
    -------
    float
        The PV of the protection leg.

    """
    dt = 1.0 / cds.freq
    periods = int(cds.tenor * cds.freq)

    pv = 0.0
    s_prev = 1.0
    for i in range(1, periods + 1):
        t = i * dt
        t_mid = t - dt / 2.0

        r_mid = curve(t_mid)
        df_mid = np.exp(-r_mid * t_mid)

        s_curr = survival_curve(t)
        default_prob = s_prev - s_curr

        pv += (1.0 - recovery_rate) * df_mid * default_prob
        s_prev = s_curr

    return float(pv * cds.notional)


def cds_par_spread(
    cds: CDS,
    curve: Callable[[float], float],
    survival_curve: Callable[[float], float],
    recovery_rate: float,
) -> float:
    """Calculate the fair par spread for a CDS (where PV premium = PV protection).

    Parameters
    ----------
    cds : CDS
        The Credit Default Swap instrument.
    curve : callable
        Continuous risk-free yield curve.
    survival_curve : callable
        Continuous survival probability curve S(t).
    recovery_rate : float
        The expected recovery rate on the underlying reference asset.

    Returns
    -------
    float
        The fair par spread (annualized).

    """
    dummy_cds = CDS(cds.notional, 1.0, cds.tenor, cds.freq)

    pv01 = cds_premium_leg(dummy_cds, curve, survival_curve) / cds.notional
    prot_leg = (
        cds_protection_leg(cds, curve, survival_curve, recovery_rate) / cds.notional
    )

    if pv01 <= 0:
        return 0.0

    return float(prot_leg / pv01)


# ISDA Standard CDS Model


def act_360(d1: datetime.date, d2: datetime.date) -> float:
    """Calculate the ACT/360 day count fraction."""
    return (d2 - d1).days / 360.0


def get_next_imm_date(d: datetime.date) -> datetime.date:
    """Get the next CDS IMM date (20th of Mar, Jun, Sep, Dec)."""
    for m in [3, 6, 9, 12]:
        if d.month < m or (d.month == m and d.day < 20):
            return datetime.date(d.year, m, 20)
    return datetime.date(d.year + 1, 3, 20)


def get_prev_imm_date(d: datetime.date) -> datetime.date:
    """Get the previous CDS IMM date."""
    for m in [12, 9, 6, 3]:
        if d.month > m or (d.month == m and d.day > 20):
            return datetime.date(d.year, m, 20)
    return datetime.date(d.year - 1, 12, 20)


def generate_imm_schedule(
    effective_date: datetime.date, maturity_date: datetime.date
) -> list[datetime.date]:
    """Generate quarterly IMM dates between effective_date and maturity_date."""
    dates = []
    curr = get_next_imm_date(effective_date)
    while curr <= maturity_date:
        dates.append(curr)
        m = curr.month + 3
        y = curr.year
        if m > 12:
            m -= 12
            y += 1
        curr = datetime.date(y, m, 20)
    return dates


def isda_premium_leg(
    valuation_date: datetime.date,
    effective_date: datetime.date,
    maturity_date: datetime.date,
    coupon: float,
    curve: Callable[[float], float],
    hazard_rate: float,
    notional: float = 1.0,
) -> float:
    """Calculate the PV of the premium leg using ISDA exact dates."""
    schedule = generate_imm_schedule(effective_date, maturity_date)
    pv = 0.0
    prev_date = effective_date
    for date in schedule:
        if date <= valuation_date:
            prev_date = date
            continue

        t_i = act_360(valuation_date, date)
        delta_i = act_360(prev_date, date)

        df = np.exp(-curve(t_i) * t_i)
        q = np.exp(-hazard_rate * t_i)

        pv += coupon * delta_i * df * q
        prev_date = date

    return float(pv * notional)


def isda_protection_leg(
    valuation_date: datetime.date,
    effective_date: datetime.date,
    maturity_date: datetime.date,
    curve: Callable[[float], float],
    hazard_rate: float,
    recovery_rate: float,
    notional: float = 1.0,
) -> float:
    """Calculate the PV of the protection leg using ISDA exact dates."""
    schedule = generate_imm_schedule(effective_date, maturity_date)
    pv = 0.0
    prev_date = effective_date

    t_prev = act_360(valuation_date, max(valuation_date, effective_date))
    q_prev = np.exp(-hazard_rate * t_prev)

    for date in schedule:
        if date <= valuation_date:
            prev_date = date
            continue

        t_i = act_360(valuation_date, date)
        t_mid = (t_prev + t_i) / 2.0

        df = np.exp(-curve(t_mid) * t_mid)
        q_curr = np.exp(-hazard_rate * t_i)

        pv += (1.0 - recovery_rate) * df * (q_prev - q_curr)

        q_prev = q_curr
        t_prev = t_i
        prev_date = date

    return float(pv * notional)


def isda_upfront_charge(
    valuation_date: datetime.date,
    effective_date: datetime.date,
    maturity_date: datetime.date,
    par_spread: float,
    standard_coupon: float,
    curve: Callable[[float], float],
    recovery_rate: float,
    notional: float = 1.0,
) -> float:
    """Calculate the ISDA standard upfront charge from a quoted par spread."""

    def objective(h: float) -> float:
        prot = isda_protection_leg(
            valuation_date, effective_date, maturity_date, curve, h, recovery_rate, 1.0
        )
        prem = isda_premium_leg(
            valuation_date, effective_date, maturity_date, par_spread, curve, h, 1.0
        )
        return prot - prem

    # Solve for implied hazard rate from par spread
    res = root_scalar(objective, bracket=[1e-5, 2.0], method="brentq")
    implied_hazard = res.root

    prot = isda_protection_leg(
        valuation_date,
        effective_date,
        maturity_date,
        curve,
        implied_hazard,
        recovery_rate,
        notional,
    )
    prem = isda_premium_leg(
        valuation_date,
        effective_date,
        maturity_date,
        standard_coupon,
        curve,
        implied_hazard,
        notional,
    )

    return float(prot - prem)


def isda_par_spread(
    valuation_date: datetime.date,
    effective_date: datetime.date,
    maturity_date: datetime.date,
    upfront_charge: float,
    standard_coupon: float,
    curve: Callable[[float], float],
    recovery_rate: float,
    notional: float = 1.0,
) -> float:
    """Calculate the implied par spread from a quoted upfront charge."""

    def objective(h: float) -> float:
        prot = isda_protection_leg(
            valuation_date,
            effective_date,
            maturity_date,
            curve,
            h,
            recovery_rate,
            notional,
        )
        prem = isda_premium_leg(
            valuation_date,
            effective_date,
            maturity_date,
            standard_coupon,
            curve,
            h,
            notional,
        )
        return (prot - prem) - upfront_charge

    # Solve for implied hazard rate from upfront charge
    res = root_scalar(objective, bracket=[1e-5, 2.0], method="brentq")
    implied_hazard = res.root

    prot_1 = isda_protection_leg(
        valuation_date,
        effective_date,
        maturity_date,
        curve,
        implied_hazard,
        recovery_rate,
        1.0,
    )
    prem_01 = isda_premium_leg(
        valuation_date, effective_date, maturity_date, 1.0, curve, implied_hazard, 1.0
    )

    return float(prot_1 / prem_01)

