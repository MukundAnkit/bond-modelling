"""Effective Duration and Convexity via numerical yield-curve bumping.

Effective measures reprice the bond after shifting the entire yield curve
(matched-curve shift), capturing any changes in expected cash flows that
arise from embedded options.  For plain-vanilla bonds they converge to the
analytical Modified Duration and Convexity as the bump size approaches zero.
"""

from src.instruments.bond import Bond
from src.instruments.pricing import price


def effective_duration(bond: Bond, yield_rate: float, bump: float = 1e-4) -> float:
    r"""Calculate the Effective Duration of a bond.

    Effective Duration measures the approximate percentage price sensitivity
    to a small parallel shift in the yield curve:

        EffD = (P_\downarrow - P_\uparrow) / (2 * bump * P_0)

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    yield_rate : float
        Current market yield (YTM) as a decimal.
    bump : float, optional
        Size of the parallel yield shift in decimal (default 1 bp = 1e-4).

    Returns
    -------
    float
        Effective Duration in years.

    """
    p0 = price(bond, yield_rate)
    p_up = price(bond, yield_rate + bump)
    p_down = price(bond, yield_rate - bump)
    return (p_down - p_up) / (2.0 * bump * p0)


def effective_convexity(bond: Bond, yield_rate: float, bump: float = 1e-4) -> float:
    r"""Calculate the Effective Convexity of a bond.

    Effective Convexity measures the curvature of the price-yield relationship
    using a central-difference approximation of the second derivative:

        EffCx = (P_\uparrow - 2 * P_0 + P_\downarrow) / (bump^2 * P_0)

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    yield_rate : float
        Current market yield (YTM) as a decimal.
    bump : float, optional
        Size of the parallel yield shift in decimal (default 1 bp = 1e-4).

    Returns
    -------
    float
        Effective Convexity in years-squared.

    """
    p0 = price(bond, yield_rate)
    p_up = price(bond, yield_rate + bump)
    p_down = price(bond, yield_rate - bump)
    return (p_up - 2.0 * p0 + p_down) / (bump * bump * p0)
