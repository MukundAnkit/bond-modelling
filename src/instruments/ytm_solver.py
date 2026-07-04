"""Yield-to-maturity solvers using generic numerical methods."""

from scipy.optimize import brentq

from src.instruments.bond import Bond
from src.instruments.pricing import price
from src.utils.math import bisection, newton_raphson


def ytm_newton(bond: Bond, target_price: float, guess: float = 0.05) -> float:
    """Solve for yield-to-maturity using the Newton-Raphson method.

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    target_price : float
        Observed market price.
    guess : float, optional
        Initial yield estimate. Default is 0.05 (5%).

    Returns
    -------
    float
        The yield-to-maturity as a decimal.

    Raises
    ------
    RuntimeError
        If the method does not converge.

    """

    def f(y: float) -> float:
        return price(bond, y) - target_price

    return newton_raphson(f, guess=guess)


def ytm_brentq(
    bond: Bond,
    target_price: float,
    lower: float = -0.05,
    upper: float = 0.50,
) -> float:
    """Solve for yield-to-maturity using Brent's method (scipy).

    Brent's method combines root bracketing, bisection, and inverse
    quadratic interpolation for guaranteed convergence on well-behaved
    functions.

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    target_price : float
        Observed market price.
    lower : float, optional
        Lower yield bound. Default is -0.05.
    upper : float, optional
        Upper yield bound. Default is 0.50.

    Returns
    -------
    float
        The yield-to-maturity as a decimal.

    Raises
    ------
    ValueError
        If the target price is not bracketed by the given bounds.

    """

    def f(y: float) -> float:
        return price(bond, y) - target_price

    f_low = f(lower)
    f_high = f(upper)
    if f_low * f_high > 0:
        raise ValueError(
            f"Root not bracketed: f({lower})={f_low:.4f}, f({upper})={f_high:.4f}"
        )

    return float(brentq(f, lower, upper))


def ytm_bisection(
    bond: Bond, target_price: float, lower: float = -0.05, upper: float = 0.50
) -> float:
    """Solve for yield-to-maturity using the bisection method.

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    target_price : float
        Observed market price.
    lower : float, optional
        Lower yield bound. Default is -0.05.
    upper : float, optional
        Upper yield bound. Default is 0.50.

    Returns
    -------
    float
        The yield-to-maturity as a decimal.

    Raises
    ------
    ValueError
        If the target price is not bracketed by the given bounds.
    RuntimeError
        If the method does not converge.

    """

    def f(y: float) -> float:
        return price(bond, y) - target_price

    return bisection(f, lower=lower, upper=upper)


def ytm_solver(
    bond: Bond,
    target_price: float,
    guess: float = 0.05,
    lower: float = -0.05,
    upper: float = 0.50,
) -> float:
    """Solve for yield-to-maturity with automatic fallback.

    Attempts Brent's method first (most robust), then Newton-Raphson,
    then bisection as a last resort.

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    target_price : float
        Observed market price.
    guess : float, optional
        Initial yield estimate for Newton-Raphson. Default is 0.05.
    lower : float, optional
        Lower bound for bisection fallback. Default is -0.05.
    upper : float, optional
        Upper bound for bisection fallback. Default is 0.50.

    Returns
    -------
    float
        The yield-to-maturity as a decimal.

    """
    try:
        return ytm_brentq(bond, target_price, lower, upper)
    except ValueError:
        try:
            return ytm_newton(bond, target_price, guess)
        except (RuntimeError, ZeroDivisionError):
            return ytm_bisection(bond, target_price, lower, upper)
