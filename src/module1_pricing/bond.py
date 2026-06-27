from dataclasses import dataclass


@dataclass
class Bond:
    face_value: float
    coupon_rate: float
    maturity: float
    freq: int = 2

    def __post_init__(self) -> None:
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
        return int(self.maturity * self.freq)

    @property
    def coupon_payment(self) -> float:
        return self.face_value * self.coupon_rate / self.freq
