"""Fixed-rate bond data structure.

Provides the Bond dataclass with input validation and convenience
properties for pricing calculations.
"""

from dataclasses import dataclass


@dataclass
class Bond:
    """A standard fixed-rate bond instrument.

    Parameters
    ----------
    face_value : float
        Principal amount (e.g. 100 or 1000).
    coupon_rate : float
        Annual coupon rate as a decimal (e.g. 0.05 for 5%).
    maturity : float
        Years to maturity.
    freq : int, optional
        Coupon payments per year (1, 2, 4, or 12). Default is 2 (semi-annual).

    """

    face_value: float
    coupon_rate: float
    maturity: float
    freq: int = 2

    def __post_init__(self) -> None:
        """Validate inputs on construction."""
        if self.face_value <= 0:
            raise ValueError("face_value must be positive")
        if self.coupon_rate < 0:
            raise ValueError("coupon_rate must be non-negative")
        if self.maturity <= 0:
            raise ValueError("maturity must be positive")
        if self.freq not in (1, 2, 4, 12):
            raise ValueError("freq must be 1, 2, 4, or 12")

    @property
    def periods(self) -> int:
        """Total number of coupon periods over the bond's life."""
        return int(self.maturity * self.freq)

    @property
    def coupon_payment(self) -> float:
        """Dollar amount of each coupon payment."""
        return self.face_value * self.coupon_rate / self.freq
