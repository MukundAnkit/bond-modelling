"""TIPS instrument module."""

from dataclasses import dataclass

import numpy as np

from src.instruments.bond import Bond


def price_tips(
    face_value: float,
    coupon_rate: float,
    maturity: float,
    real_ytm: float,
    index_ratio: float,
    freq: int = 2,
) -> float:
    """Price a TIPS bond given its real yield to maturity.

    Parameters
    ----------
    face_value : float
        Face value of the bond.
    coupon_rate : float
        Real coupon rate (annual).
    maturity : float
        Time to maturity in years.
    real_ytm : float
        Real yield to maturity (annual).
    index_ratio : float
        Current index ratio (CPI_current / CPI_base).
    freq : int, optional
        Coupon frequency per year. Default is 2.

    Returns
    -------
    float
        Invoice price of the TIPS bond.

    """
    periods = int(maturity * freq)
    coupon = coupon_rate / freq
    ytm = real_ytm / freq

    periods_arr = np.arange(1, periods + 1)
    pv_coupons = float(np.sum(coupon * face_value / (1 + ytm) ** periods_arr))
    pv_principal = face_value / (1 + ytm) ** periods

    return float((pv_coupons + pv_principal) * index_ratio)


@dataclass
class TIPS(Bond):
    """Treasury Inflation-Protected Security (TIPS).

    Inherits from standard Bond, adding Base CPI and modeling
    for inflation adjustment.
    """

    base_cpi: float = 100.0

    def __post_init__(self) -> None:
        """Validate inputs on construction."""
        super().__post_init__()
        if self.base_cpi <= 0:
            raise ValueError("base_cpi must be positive")

    def inflation_adjusted_cashflows(
        self, index_ratios: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Generate inflation-adjusted cash flows for the TIPS.

        Parameters
        ----------
        index_ratios : np.ndarray
            Index ratios for each coupon payment date.
            Must match the number of periods (self.periods).

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            A tuple of (times_in_periods, adjusted_cash_flow_amounts).

        """
        if len(index_ratios) != self.periods:
            raise ValueError("Must provide an index ratio for each period")

        t = np.arange(1, self.periods + 1)

        # Real coupons
        cf = np.full(self.periods, self.coupon_payment)
        adjusted_cf = cf * index_ratios

        # Deflation floor applied to principal at maturity
        # Principal is max(face_value, face_value * index_ratio)
        principal_ratio = max(1.0, float(index_ratios[-1]))
        adjusted_cf[-1] += self.face_value * principal_ratio

        return t, adjusted_cf
