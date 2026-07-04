class FloatingRateNote:
    def __init__(self, notional, reference_rate, quoted_margin, payment_frequency, maturity_years, has_floor=False, floor_rate=0.0):
        self.notional = notional
        self.reference_rate = reference_rate
        self.quoted_margin = quoted_margin
        self.payment_frequency = payment_frequency
        self.maturity_years = maturity_years
        self.has_floor = has_floor
        self.floor_rate = floor_rate

    def price(self, discount_margin):
        # TODO: Implement pricing logic
        return 0.0
