from typing import Callable

from src.module1_pricing.bond import Bond
from src.module1_pricing.pricing import price

TOLERANCE = 1e-6
MAX_ITER = 500


def _price_diff(bond: Bond, target_price: float, y: float) -> float:
    return price(bond, y) - target_price


def ytm_newton(bond: Bond, target_price: float, guess: float = 0.05) -> float:
    y = guess
    for _ in range(MAX_ITER):
        p = price(bond, y)
        f = p - target_price
        if abs(f) < TOLERANCE:
            return y
        derivative = _dv01_approx(bond, y)
        if abs(derivative) < 1e-12:
            break
        y -= f / derivative
    raise RuntimeError("Newton-Raphson did not converge")


def _dv01_approx(bond: Bond, y: float, eps: float = 1e-6) -> float:
    return (price(bond, y + eps) - price(bond, y - eps)) / (2 * eps)


def ytm_bisection(
    bond: Bond, target_price: float, lower: float = -0.05, upper: float = 0.50
) -> float:
    f_low = _price_diff(bond, target_price, lower)
    f_high = _price_diff(bond, target_price, upper)
    if f_low * f_high > 0:
        raise ValueError(
            f"YTM not bracketed: price({lower})={f_low + target_price:.4f}, "
            f"price({upper})={f_high + target_price:.4f}, target={target_price:.4f}"
        )
    for _ in range(MAX_ITER):
        mid = (lower + upper) / 2
        f_mid = _price_diff(bond, target_price, mid)
        if abs(f_mid) < TOLERANCE:
            return mid
        if f_low * f_mid <= 0:
            upper = mid
            f_high = f_mid
        else:
            lower = mid
            f_low = f_mid
    raise RuntimeError("Bisection did not converge")


def ytm_solver(
    bond: Bond,
    target_price: float,
    guess: float = 0.05,
    lower: float = -0.05,
    upper: float = 0.50,
) -> float:
    try:
        return ytm_newton(bond, target_price, guess)
    except (RuntimeError, ZeroDivisionError):
        return ytm_bisection(bond, target_price, lower, upper)
