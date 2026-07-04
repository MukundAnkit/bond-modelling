"""Present-value pricing for fixed-rate bonds."""

import numpy as np

from src.instruments.bond import Bond
from src.utils.cashflows import generate_cashflows


def price(bond: Bond, yield_rate: float) -> float:
    """Calculate the present value of all future bond cash flows.

    Parameters
    ----------
    bond : Bond
        The bond instrument to price.
    yield_rate : float
        Market yield (YTM) as a decimal.

    Returns
    -------
    float
        The bond's theoretical price (present value).

    """
    rate_per_period = yield_rate / bond.freq
    t, cf = generate_cashflows(bond)

    pv = np.sum(cf / (1 + rate_per_period) ** t)
    return float(round(pv, 12))


def zero_coupon_price(
    face_value: float,
    yield_rate: float,
    maturity: float,
    compounding_freq: int = 2,
) -> float:
    """Calculate the price of a zero-coupon bond.

    Uses the specified compounding convention (default semi-annual,
    the US Treasury STRIPS standard for Bond Equivalent Yield).

    Parameters
    ----------
    face_value : float
        Principal amount.
    yield_rate : float
        Market yield (YTM) as a decimal.
    maturity : float
        Years to maturity.
    compounding_freq : int, optional
        Compounding periods per year. Default is 2 (semi-annual).

    Returns
    -------
    float
        The zero-coupon bond price.

    """
    return float(
        face_value
        / (1 + yield_rate / compounding_freq) ** (compounding_freq * maturity)
    )


def accrued_interest(
    coupon_payment: float,
    fraction_of_period: float,
) -> float:
    """Calculate accrued interest since the last coupon date.

    Parameters
    ----------
    coupon_payment : float
        Dollar amount of each coupon payment.
    fraction_of_period : float
        Fraction of the coupon period that has elapsed
        (0 = last coupon just paid, 1 = next coupon imminent).

    Returns
    -------
    float
        Accrued interest amount.

    """
    return coupon_payment * fraction_of_period


def dirty_price(clean_price: float, accrued: float) -> float:
    """Calculate the dirty (invoice) price from clean price and accrued interest.

    Parameters
    ----------
    clean_price : float
        Quoted clean price.
    accrued : float
        Accrued interest amount.

    Returns
    -------
    float
        Dirty (invoice) price.

    """
    return clean_price + accrued


def clean_price_from_dirty(dirty_price: float, accrued: float) -> float:
    """Calculate the clean (quoted) price from dirty price and accrued interest.

    Parameters
    ----------
    dirty_price : float
        Invoice price.
    accrued : float
        Accrued interest amount.

    Returns
    -------
    float
        Clean (quoted) price.

    """
    return dirty_price - accrued
