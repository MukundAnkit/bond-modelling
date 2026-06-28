"""Dollar-based risk measures: Dollar Duration, DV01, and Dollar Convexity."""

from src.instruments.bond import Bond
from src.instruments.pricing import price
from src.risk.convexity import convexity
from src.risk.duration import modified_duration


def dollar_duration(bond: Bond, yield_rate: float) -> float:
    """Calculate the Dollar Duration of a fixed-rate bond.

    Dollar Duration measures the absolute (dollar) price sensitivity to
    a 1-unit change in yield: DD = ModD × P.

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    yield_rate : float
        Market yield (YTM) as a decimal.

    Returns
    -------
    float
        Dollar Duration in price units per unit yield.

    """
    p = price(bond, yield_rate)
    modd = modified_duration(bond, yield_rate)
    return modd * p


def dv01(bond: Bond, yield_rate: float) -> float:
    """Calculate the DV01 (Dollar Value of a Basis Point) of a bond.

    DV01 (also known as PVBP) is the absolute price change for a 1 basis
    point (0.01%) change in yield: DV01 = DD / 10,000.

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    yield_rate : float
        Market yield (YTM) as a decimal.

    Returns
    -------
    float
        DV01 in price units per basis point.

    """
    return dollar_duration(bond, yield_rate) / 10_000


def dollar_convexity(bond: Bond, yield_rate: float) -> float:
    """Calculate the Dollar Convexity of a fixed-rate bond.

    Dollar Convexity is the absolute curvature of the price-yield
    relationship: DC = Cx × P.

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    yield_rate : float
        Market yield (YTM) as a decimal.

    Returns
    -------
    float
        Dollar Convexity in price units per yield-squared.

    """
    p = price(bond, yield_rate)
    cx = convexity(bond, yield_rate)
    return cx * p
