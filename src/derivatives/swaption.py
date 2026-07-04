"""Swaption pricing module."""

from collections.abc import Callable
from dataclasses import dataclass

from scipy.optimize import root_scalar

from src.derivatives import aad
from src.derivatives.cap_floor import vasicek_zcb_option
from src.derivatives.swap import InterestRateSwap
from src.models.stochastic import VasicekModel


@dataclass
class Swaption:
    """European Swaption."""

    swap: InterestRateSwap
    expiry: float
    option_type: str  # 'payer' or 'receiver'

    def __post_init__(self) -> None:  # noqa: D105
        if self.option_type not in ["payer", "receiver"]:
            raise ValueError("option_type must be 'payer' or 'receiver'")
        if self.expiry <= 0.0:
            raise ValueError("Expiry must be strictly positive")
        if self.expiry >= self.swap.tenor:
            raise ValueError("Expiry must be before the underlying swap maturity")


def price_swaption_jamshidian(
    swaption: Swaption, model: VasicekModel, r_t: float
) -> float:
    """Prices a European Swaption under the Vasicek model using Jamshidian's Trick.

    Parameters
    ----------
    swaption : Swaption
        The swaption to price.
    model : VasicekModel
        The Vasicek short-rate model.
    r_t : float
        Current short rate at time 0.

    Returns
    -------
    float
        Present value of the Swaption.

    """
    # The underlying swap starts at swaption.expiry and matures at swaption.swap.tenor.
    # Note: swap.tenor here is usually the absolute maturity from t=0.
    # We will assume swaption.swap.tenor is the ABSOLUTE maturity from t=0.

    # Let's define the cashflows of the underlying fixed leg + notional at maturity
    # For a Payer Swaption (pay fixed K, receive float), the payoff at T is:
    # max( 1 - P(T, T_n) - K * dt * sum P(T, T_i), 0 )
    # = max( 1 - sum(c_i P(T, T_i)), 0 )
    # which is a put option on a coupon-bearing bond with strike 1.

    dt = 1.0 / swaption.swap.freq
    # The swap payments happen after expiry.
    payment_times = []
    t = swaption.expiry + dt
    while t <= swaption.swap.tenor + 1e-6:
        payment_times.append(t)
        t += dt

    if not payment_times:
        return 0.0

    c = [swaption.swap.fixed_rate * dt] * len(payment_times)
    c[-1] += 1.0  # Add principal

    # 1. Find critical rate r* at expiry T such that the coupon bond price is 1.0
    T = swaption.expiry  # noqa: N806

    def cb_price_at_T(r: float) -> float:  # noqa: N802
        price = 0.0
        for ci, Ti in zip(c, payment_times, strict=False):  # noqa: N806
            price += float(ci * model.zcb_price(r, Ti - T))
        return price - 1.0

    # Find root r*
    res = root_scalar(cb_price_at_T, bracket=[-0.5, 0.5], method="brentq")
    r_star = res.root

    # 2. Calculate individual strikes X_i = P(T, T_i; r*)
    X = [model.zcb_price(r_star, Ti - T) for Ti in payment_times]  # noqa: N806

    # 3. Sum up the options on ZCBs
    # Payer Swaption = Put on coupon bond = sum( ci * Put(ZCB_i) )
    # Receiver Swaption = Call on coupon bond = sum( ci * Call(ZCB_i) )
    opt_type = "put" if swaption.option_type == "payer" else "call"

    pv = 0.0
    for ci, Ti, Xi in zip(c, payment_times, X, strict=False):  # noqa: N806
        zcb_opt = vasicek_zcb_option(model, r_t, 0.0, T, Ti, float(Xi), opt_type)
        pv += ci * zcb_opt

    return pv * swaption.swap.notional


def price_swaption_bachelier(
    swaption: Swaption,
    discount_curve: Callable[[float], float],
    forward_curve: Callable[[float], float] | None = None,
    vol: float = 0.0,
    sabr_params: dict | None = None,
) -> float:
    """Price a European Swaption using Bachelier and SABR models.

    Parameters
    ----------
    swaption : Swaption
        The swaption to price.
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
        The PV of the Swaption.

    """
    if forward_curve is None:
        forward_curve = discount_curve

    dt = 1.0 / swaption.swap.freq
    payment_times = []
    t = swaption.expiry + dt
    while t <= swaption.swap.tenor + 1e-6:
        payment_times.append(t)
        t += dt

    if not payment_times:
        return 0.0

    # Calculate annuity A = sum(dt * Z_i_d)
    annuity = 0.0
    float_pv = 0.0

    t_prev = swaption.expiry
    for ti in payment_times:
        yi_d = discount_curve(ti)
        z_d = aad.exp(-yi_d * ti)
        annuity += dt * z_d

        # Forward rate implied from forward_curve
        y_f_prev = forward_curve(t_prev)
        z_f_prev = aad.exp(-y_f_prev * t_prev)

        y_f = forward_curve(ti)
        z_f = aad.exp(-y_f * ti)

        if float(z_f) > 0:
            fwd_rate = (z_f_prev / z_f - 1.0) / dt
        else:
            fwd_rate = 0.0

        float_pv += fwd_rate * dt * z_d
        t_prev = ti

    s_fwd = float_pv / annuity if annuity > 0 else 0.0

    # Calculate implied volatility
    if sabr_params is not None:
        from src.derivatives.sabr import sabr_normal_vol
        implied_vol = sabr_normal_vol(
            fwd=s_fwd,
            strike=swaption.swap.fixed_rate,
            t_exp=swaption.expiry,
            alpha=sabr_params.get("alpha", vol),
            rho=sabr_params.get("rho", 0.0),
            nu=sabr_params.get("nu", 0.1),
        )
    else:
        implied_vol = vol

    is_call = swaption.option_type == "payer"

    # Swaption price = N * A * Bachelier(S, K, vol_N)
    from src.derivatives.bachelier import bachelier_formula

    opt = bachelier_formula(
        fwd=s_fwd,
        strike=swaption.swap.fixed_rate,
        t_exp=swaption.expiry,
        vol=implied_vol,
        df=1.0,  # df is handled by annuity outside
        is_call=is_call,
    )

    return swaption.swap.notional * annuity * opt
