"""Interest rate caps and floors implementation."""
from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from src.derivatives.black import black_formula
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

    P_t_T = model.zcb_price(r_t, T - t)
    P_t_S = model.zcb_price(r_t, S - t)

    if np.isclose(a, 0):
        # limiting case for a -> 0
        B_T_S = S - T
        var = sigma**2 * (T - t)
    else:
        B_T_S = (1.0 - np.exp(-a * (S - T))) / a
        var = (1.0 - np.exp(-2.0 * a * (T - t))) / (2.0 * a)

    sigma_P = sigma * B_T_S * np.sqrt(var)

    if sigma_P == 0.0:
        if option_type == 'call':
            return max(0.0, P_t_S - X * P_t_T)
        else:
            return max(0.0, X * P_t_T - P_t_S)

    d1 = (np.log(P_t_S / (X * P_t_T)) / sigma_P) + 0.5 * sigma_P
    d2 = d1 - sigma_P

    if option_type == 'call':
        return P_t_S * norm.cdf(d1) - X * P_t_T * norm.cdf(d2)
    elif option_type == 'put':
        return X * P_t_T * norm.cdf(-d2) - P_t_S * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

def cap_floor_pv(instrument, model: VasicekModel, r_t: float) -> float:
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

    # Caplets/Floorlets start from the first period (paying at T_2 based on rate set at T_1)
    for i in range(1, periods + 1):
        T1 = (i - 1) * dt  # noqa: N806
        T2 = i * dt  # noqa: N806

        # The first caplet (T1=0) is typically known and just a discounted cashflow if L > K,
        # but in standard valuation we price the option from T1>0.
        # We will price it for all i; if T1=0, variance is 0 and it becomes intrinsic value.
        X = 1.0 / (1.0 + instrument.strike * dt)  # noqa: N806
        qty = instrument.notional * (1.0 + instrument.strike * dt)

        if isinstance(instrument, Cap):
            pv += vasicek_zcb_option(model, r_t, 0.0, T1, T2, float(X), "put") * qty
        elif isinstance(instrument, Floor):
            pv += vasicek_zcb_option(model, r_t, 0.0, T1, T2, float(X), "call") * qty
        else:
            raise TypeError("instrument must be Cap or Floor")


    return pv

def cap_floor_black(instrument, curve, vol: float) -> float:
    """Price a Cap or Floor using Black's (1976) model.

    Parameters
    ----------
    instrument : Cap | Floor
        The instrument to price.
    curve : callable
        Continuous yield curve.
    vol : float
        Implied Black volatility (log-normal).
        
    Returns
    -------
    float
        The PV of the Cap or Floor.
    """
    dt = 1.0 / instrument.freq
    periods = int(instrument.tenor * instrument.freq)
    
    pv = 0.0
    
    for i in range(1, periods + 1):
        T1 = (i - 1) * dt  # noqa: N806
        T2 = i * dt  # noqa: N806
        
        y1 = curve(T1)
        z1 = np.exp(-y1 * T1)
        y2 = curve(T2)
        z2 = np.exp(-y2 * T2)
        
        # Forward LIBOR rate for [T1, T2]
        if z2 > 0:
            F = (z1 / z2 - 1.0) / dt  # noqa: N806
        else:
            F = 0.0  # noqa: N806
            
        df = z2 * dt
        
        is_cap = isinstance(instrument, Cap)
        # Caplet is a call on the forward rate, Floorlet is a put
        pv += instrument.notional * black_formula(
            F=F, 
            K=instrument.strike, 
            T=T1,  # expiry is T1
            sigma=vol, 
            df=df, 
            is_call=is_cap
        )
        
    return pv
