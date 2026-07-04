class BinomialTree:
    """A simple binomial tree for interest rate modelling."""

    def __init__(
        self, r0: float, volatility: float, time_step: float, periods: int
    ) -> None:
        self.r0 = r0
        self.volatility = volatility
        self.time_step = time_step
        self.periods = periods

    def build_tree(self) -> list[list[float]]:
        """Build the binomial interest rate tree."""
        import numpy as np

        u = np.exp(self.volatility * np.sqrt(self.time_step))
        rates = []
        for i in range(self.periods + 1):
            step_rates = []
            for j in range(i + 1):
                r = self.r0 * (u ** (2 * j - i))
                step_rates.append(r)
            rates.append(step_rates)
        return rates

    def get_probabilities(self) -> dict[str, float]:
        """Get risk-neutral probabilities for up and down movements."""
        return {"p_up": 0.5, "p_down": 0.5}

    def price_zero_coupon_bond(self, face_value: float) -> float:
        """Price a zero-coupon bond using the binomial tree."""
        rates = self.build_tree()
        probs = self.get_probabilities()
        p_up = probs["p_up"]
        p_down = probs["p_down"]
        dt = self.time_step

        values = [face_value for _ in range(self.periods + 1)]

        for i in range(self.periods - 1, -1, -1):
            next_values = []
            for j in range(i + 1):
                ev = p_up * values[j + 1] + p_down * values[j]
                r_ij = rates[i][j]
                v = ev / (1 + r_ij * dt)
                next_values.append(v)
            values = next_values

        return values[0]
