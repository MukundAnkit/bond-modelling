"""Interest-rate shock simulation using Taylor series expansion."""

from src.instruments.bond import Bond
from src.instruments.pricing import price
from src.risk.convexity import convexity
from src.risk.duration import modified_duration


def price_shock(bond: Bond, yield_rate: float, delta_y: float) -> float:
    """Estimate the price change for a given yield shock.

    Uses a second-order Taylor expansion (modified duration + convexity).

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    yield_rate : float
        Current market yield (YTM) as a decimal.
    delta_y : float
        Yield shock in decimal form (e.g. 0.01 for +100 bps).

    Returns
    -------
    float
        Estimated change in price (ΔP).

    """
    p = price(bond, yield_rate)
    modd = modified_duration(bond, yield_rate)
    cx = convexity(bond, yield_rate)
    return -modd * p * delta_y + 0.5 * cx * p * delta_y * delta_y


def shocked_price(bond: Bond, yield_rate: float, delta_y: float) -> float:
    r"""Estimate the new bond price after a yield shock.

    .. math::

        P_{\text{new}} \approx P + \Delta P

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    yield_rate : float
        Current market yield (YTM) as a decimal.
    delta_y : float
        Yield shock in decimal form (e.g. 0.01 for +100 bps).

    Returns
    -------
    float
        Estimated new price after the shock.

    """
    p = price(bond, yield_rate)
    return p + price_shock(bond, yield_rate, delta_y)
