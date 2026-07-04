class FloatingRateNote:
    """A Floating Rate Note instrument."""

    def __init__(
        self,
        notional: float,
        reference_rate: float,
        quoted_margin: float,
        payment_frequency: int,
        maturity_years: float,
        has_floor: bool = False,
        floor_rate: float = 0.0,
    ) -> None:
        self.notional = notional
        self.reference_rate = reference_rate
        self.quoted_margin = quoted_margin
        self.payment_frequency = payment_frequency
        self.maturity_years = maturity_years
        self.has_floor = has_floor
        self.floor_rate = floor_rate

    def price(self, discount_margin: float) -> float:
        """Calculate the present value of the FRN using the discount margin."""
        coupon_rate = self.reference_rate + self.quoted_margin
        if self.has_floor:
            coupon_rate = max(coupon_rate, self.floor_rate)

        discount_rate = self.reference_rate + discount_margin
        if self.has_floor and discount_rate < 0:
            discount_rate = max(discount_rate, self.floor_rate)

        n_periods = int(self.maturity_years * self.payment_frequency)
        dt = 1.0 / self.payment_frequency

        price = 0.0
        for i in range(1, n_periods + 1):
            cf = self.notional * coupon_rate * dt
            if i == n_periods:
                cf += self.notional
            price += cf / ((1 + discount_rate * dt) ** i)

        return price
