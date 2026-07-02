"""Hull-White 1-Factor model analytical formulas."""

from collections.abc import Callable

import numpy as np

from src.trees.trinomial_tree import HWTree


class HullWhite1F:
    """Hull-White 1-Factor Model: dr(t) = (theta(t) - a * r(t))dt + sigma * dW(t)."""

    def __init__(
        self, a: float, sigma: float, forward_rate_curve: Callable[[float], float]
    ):
        """Initialize the Hull-White model."""
        self.a = a
        self.sigma = sigma
        self.forward_rate_curve = forward_rate_curve

    def b_factor(self, t: float, t_end: float) -> float:
        """Calculate B(t, T) in the affine zero-coupon bond price formula."""
        if self.a == 0:
            return t_end - t
        return float((1.0 - np.exp(-self.a * (t_end - t))) / self.a)

    def a_factor(self, t: float, t_end: float, p_0_t: float, p_0_end: float) -> float:
        """Calculate A(t, T) in the affine zero-coupon bond price formula.

        Args:
            t: Current time.
            t_end: Maturity time.
            p_0_t: P(0, t).
            p_0_end: P(0, T).

        """
        b_val = self.b_factor(t, t_end)
        f_t = self.forward_rate_curve(t)

        term1 = p_0_end / p_0_t
        term2 = b_val * f_t
        term3 = (
            (self.sigma**2 / (4 * self.a))
            * (1.0 - np.exp(-2 * self.a * t))
            * (b_val**2)
        )

        return float(term1 * np.exp(term2 - term3))

    def zero_coupon_bond(
        self, t: float, t_end: float, r_t: float, p_0_t: float, p_0_end: float
    ) -> float:
        """Calculate price of a zero coupon bond P(t, T)."""
        if t >= t_end:
            return 1.0
        a_val = self.a_factor(t, t_end, p_0_t, p_0_end)
        b_val = self.b_factor(t, t_end)
        return float(a_val * np.exp(-b_val * r_t))


class HullWhiteTree(HWTree):
    """Hull-White Trinomial Tree (alias for HWTree)."""

    pass
