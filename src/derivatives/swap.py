"""Interest rate swap implementation."""

from collections.abc import Callable
from dataclasses import dataclass

from src.derivatives import aad


@dataclass
class InterestRateSwap:
    """Plain Vanilla Interest Rate Swap."""

    notional: float
    fixed_rate: float
    tenor: float  # in years
    freq: int = 2  # payments per year


def swap_rate(
    swap: InterestRateSwap,
    discount_curve: Callable[[float], float],
    forward_curve: Callable[[float], float] | None = None,
):
    """Calculate the par swap rate for given swap structure and continuous yield curves.

    In a multi-curve framework, the forward rate is determined by the forward_curve,
    and the cashflows are discounted using the discount_curve.

    Parameters
    ----------
    swap : InterestRateSwap
        The swap structure (ignores the fixed_rate in the object).
    discount_curve : callable
        Returns continuous yield y(t) for discounting when called with time t (in years).
    forward_curve : callable, optional
        Returns continuous yield y(t) for forward rate estimation. Defaults to discount_curve.

    Returns
    -------
    float or Dual
        The par swap rate (annualized).

    """
    if forward_curve is None:
        forward_curve = discount_curve

    dt = 1.0 / swap.freq
    periods = int(swap.tenor * swap.freq)

    pv01 = 0.0
    float_pv = 0.0

    for i in range(1, periods + 1):
        t = i * dt
        t_prev = (i - 1) * dt

        # Discount factor Z(t) from discount_curve
        y_d = discount_curve(t)
        z_d = aad.exp(-y_d * t)

        pv01 += z_d * dt

        # Forward rate implied from forward_curve
        if i == 1:
            z_f_prev = 1.0
        else:
            y_f_prev = forward_curve(t_prev)
            z_f_prev = aad.exp(-y_f_prev * t_prev)

        y_f = forward_curve(t)
        z_f = aad.exp(-y_f * t)

        if float(z_f) > 0:
            fwd_rate = (z_f_prev / z_f - 1.0) / dt
        else:
            fwd_rate = 0.0

        float_pv += fwd_rate * dt * z_d

    return float(float_pv / pv01)


def swap_pv(
    swap: InterestRateSwap,
    discount_curve: Callable[[float], float],
    forward_curve: Callable[[float], float] | None = None,
    position: str = "receiver",
):
    """Calculate the Present Value (PV) of the Interest Rate Swap.

    Parameters
    ----------
    swap : InterestRateSwap
        The swap to price.
    discount_curve : callable
        Continuous yield curve for discounting.
    forward_curve : callable, optional
        Continuous yield curve for forward rates. Defaults to discount_curve.
    position : str
        "receiver" (receives fixed, pays float) or "payer" (pays fixed, receives float).

    Returns
    -------
    float or Dual
        The net present value of the swap from the perspective of the chosen position.

    """
    if position not in ["receiver", "payer"]:
        raise ValueError("Position must be 'receiver' or 'payer'.")

    if forward_curve is None:
        forward_curve = discount_curve

    dt = 1.0 / swap.freq
    periods = int(swap.tenor * swap.freq)

    pv_fixed = 0.0
    pv_floating = 0.0

    for i in range(1, periods + 1):
        t = i * dt
        t_prev = (i - 1) * dt

        # Discount factor Z(t) from discount_curve
        y_d = discount_curve(t)
        z_d = aad.exp(-y_d * t)

        pv_fixed += swap.notional * swap.fixed_rate * dt * z_d

        # Forward rate implied from forward_curve
        if i == 1:
            z_f_prev = 1.0
        else:
            y_f_prev = forward_curve(t_prev)
            z_f_prev = aad.exp(-y_f_prev * t_prev)

        y_f = forward_curve(t)
        z_f = aad.exp(-y_f * t)

        if float(z_f) > 0:
            fwd_rate = (z_f_prev / z_f - 1.0) / dt
        else:
            fwd_rate = 0.0

        pv_floating += swap.notional * fwd_rate * dt * z_d

    if position == "receiver":
        return pv_fixed - pv_floating
    else:
        return pv_floating - pv_fixed
