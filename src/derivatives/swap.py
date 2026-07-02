"""Interest rate swap implementation."""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np


@dataclass
class InterestRateSwap:
    """Plain Vanilla Interest Rate Swap."""

    notional: float
    fixed_rate: float
    tenor: float  # in years
    freq: int = 2  # payments per year


def swap_rate(swap: InterestRateSwap, curve: Callable[[float], float]) -> float:
    """Calculate the par swap rate for given swap structure and continuous yield curve.

    In a single-curve framework, the PV of the floating leg is Notional * (1 - Z(T)).
    The PV of a basis point on the fixed leg (PV01 / Notional) is sum(Z(t) * dt).

    Parameters
    ----------
    swap : InterestRateSwap
        The swap structure (ignores the fixed_rate in the object).
    curve : callable
        Returns continuous yield y(t) when called with time t (in years).

    Returns
    -------
    float
        The par swap rate (annualized).

    """
    dt = 1.0 / swap.freq
    periods = int(swap.tenor * swap.freq)

    pv01 = 0.0
    for i in range(1, periods + 1):
        t = i * dt
        y = curve(t)
        # Discount factor Z(t) = exp(-y * t)
        z = np.exp(-y * t)
        pv01 += z * dt

    # Discount factor at maturity
    y_T = curve(swap.tenor)  # noqa: N806
    z_T = np.exp(-y_T * swap.tenor)  # noqa: N806

    return float((1.0 - z_T) / pv01)


def swap_pv(
    swap: InterestRateSwap, curve: Callable[[float], float], position: str = "receiver"
) -> float:
    """Calculate the Present Value (PV) of the Interest Rate Swap.

    Parameters
    ----------
    swap : InterestRateSwap
        The swap to price.
    curve : callable
        Continuous yield curve.
    position : str
        "receiver" (receives fixed, pays float) or "payer" (pays fixed, receives float).

    Returns
    -------
    float
        The net present value of the swap from the perspective of the chosen position.

    """
    if position not in ["receiver", "payer"]:
        raise ValueError("Position must be 'receiver' or 'payer'.")

    dt = 1.0 / swap.freq
    periods = int(swap.tenor * swap.freq)

    pv_fixed = 0.0
    for i in range(1, periods + 1):
        t = i * dt
        y = curve(t)
        z = np.exp(-y * t)
        pv_fixed += swap.notional * swap.fixed_rate * dt * z

    # Floating leg PV in a single-curve framework
    y_T = curve(swap.tenor)  # noqa: N806
    z_T = np.exp(-y_T * swap.tenor)  # noqa: N806
    pv_floating = swap.notional * (1.0 - z_T)

    if position == "receiver":
        return float(pv_fixed - pv_floating)
    else:
        return float(pv_floating - pv_fixed)
