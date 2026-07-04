"""Interest rate caps and floors implementation."""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from src.derivatives import aad
from src.models.stochastic import VasicekModel


@dataclass
class Cap:
    """Interest Rate Cap."""

    notional: float
    strike: float
    tenor: float
    freq: int = 2


@dataclass
class Floor:
    """Interest Rate Floor."""

    notional: float
    strike: float
    tenor: float
    freq: int = 2


def vasicek_zcb_option(
    model: VasicekModel,
    r_t: float,
    t: float,
    T: float,  # noqa: N803
    S: float,  # noqa: N803
    X: float,  # noqa: N803
    option_type: str,
) -> float:
    """Price a European option on a Zero-Coupon Bond under the Vasicek model.

    Parameters
    ----------
    model : VasicekModel
        The Vasicek short-rate model.
    r_t : float
        Current short rate at time t.
    t : float
        Current time.
    T : float
        Option expiry time.
    S : float
        Underlying ZCB maturity (S > T).
    X : float
        Strike price.
    option_type : str
        'call' or 'put'.

    Returns
    -------
    float
        The option price.

    """
    a = model.a
    sigma = model.sigma

    p_t_T = model.zcb_price(r_t, T - t)  # noqa: N806
    p_t_S = model.zcb_price(r_t, S - t)  # noqa: N806

    if np.isclose(a, 0):
        # limiting case for a -> 0
        b_T_S = S - T  # noqa: N806
        var = sigma**2 * (T - t)
    else:
        b_T_S = (1.0 - np.exp(-a * (S - T))) / a  # noqa: N806
        var = (1.0 - np.exp(-2.0 * a * (T - t))) / (2.0 * a)

    sigma_p = sigma * b_T_S * np.sqrt(var)  # noqa: N806

    if sigma_p == 0.0:
        if option_type == "call":
            return float(max(0.0, p_t_S - X * p_t_T))
        else:
            return float(max(0.0, X * p_t_T - p_t_S))

    d1 = (np.log(p_t_S / (X * p_t_T)) / sigma_p) + 0.5 * sigma_p
    d2 = d1 - sigma_p

    if option_type == "call":
        return float(p_t_S * norm.cdf(d1) - X * p_t_T * norm.cdf(d2))
    elif option_type == "put":
        return float(X * p_t_T * norm.cdf(-d2) - p_t_S * norm.cdf(-d1))
    else:
        raise ValueError("option_type must be 'call' or 'put'")


def cap_floor_pv(instrument: Cap | Floor, model: VasicekModel, r_t: float) -> float:
    """Price a Cap or Floor under the Vasicek model.

    Parameters
    ----------
    instrument : Cap | Floor
        The Cap or Floor to price.
    model : VasicekModel
        The Vasicek short-rate model.
    r_t : float
        Current short rate.

    Returns
    -------
    float
        Present value of the Cap or Floor.

    """
    dt = 1.0 / instrument.freq
    periods = int(instrument.tenor * instrument.freq)

    pv = 0.0

    # Caplets/Floorlets: first period pays at T_2 based on rate set at T_1
    for i in range(1, periods + 1):
        T1 = (i - 1) * dt  # noqa: N806
        T2 = i * dt  # noqa: N806

        # The first caplet (T1=0) is typically just a discounted cashflow if L > K,
        # but standard valuation prices the option from T1>0.
        # We price it for all i; T1=0 gives variance=0 and becomes intrinsic value.
        X = 1.0 / (1.0 + instrument.strike * dt)  # noqa: N806
        qty = instrument.notional * (1.0 + instrument.strike * dt)

        if isinstance(instrument, Cap):
            pv += vasicek_zcb_option(model, r_t, 0.0, T1, T2, float(X), "put") * qty
        elif isinstance(instrument, Floor):
            pv += vasicek_zcb_option(model, r_t, 0.0, T1, T2, float(X), "call") * qty
        else:
            raise TypeError("instrument must be Cap or Floor")

    return pv


def cap_floor_bachelier(
    instrument: Cap | Floor,
    discount_curve: Callable[[float], float],
    forward_curve: Callable[[float], float] | None = None,
    vol: float = 0.0,
    sabr_params: dict | None = None,
) -> float:
    """Price a Cap or Floor using Bachelier and SABR models.

    Parameters
    ----------
    instrument : Cap | Floor
        The instrument to price.
    discount_curve : callable
        Continuous yield curve for discounting.
    forward_curve : callable, optional
        Continuous yield curve for forward rates. Defaults to discount_curve.
    vol : float, optional
        Normal implied volatility (used if sabr_params is None).
    sabr_params : dict, optional
        Dictionary with keys 'alpha', 'rho', 'nu' for SABR model. If provided,
        vol is computed using the SABR normal volatility formula.

    Returns
    -------
    float
        The PV of the Cap or Floor.

    """
    if forward_curve is None:
        forward_curve = discount_curve

    dt = 1.0 / instrument.freq
    periods = int(instrument.tenor * instrument.freq)

    pv = 0.0

    from src.derivatives.bachelier import bachelier_formula

    for i in range(1, periods + 1):
        T1 = (i - 1) * dt  # noqa: N806
        T2 = i * dt  # noqa: N806

        y1_f = forward_curve(T1)
        z1_f = aad.exp(-y1_f * T1)
        y2_f = forward_curve(T2)
        z2_f = aad.exp(-y2_f * T2)

        # Forward LIBOR rate for [T1, T2] from forward_curve
        fwd = (z1_f / z2_f - 1.0) / dt if float(z2_f) > 0 else 0.0  # noqa: N806

        y2_d = discount_curve(T2)
        z2_d = aad.exp(-y2_d * T2)
        df = z2_d * dt

        # Calculate implied volatility
        if sabr_params is not None:
            from src.derivatives.sabr import sabr_normal_vol
            implied_vol = sabr_normal_vol(
                fwd=fwd,
                strike=instrument.strike,
                t_exp=T1,
                alpha=sabr_params.get("alpha", vol),
                rho=sabr_params.get("rho", 0.0),
                nu=sabr_params.get("nu", 0.1),
            )
        else:
            implied_vol = vol

        is_cap = isinstance(instrument, Cap)
        # Caplet is a call on the forward rate, Floorlet is a put
        pv += instrument.notional * bachelier_formula(
            fwd=fwd,
            strike=instrument.strike,
            t_exp=T1,  # expiry is T1
            vol=implied_vol,
            df=df,
            is_call=is_cap,
        )

    return pv
