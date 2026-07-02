"""Credit Default Swap (CDS) pricing module."""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np


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
