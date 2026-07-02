# ruff: noqa
# mypy: ignore-errors
import numpy as np


class ConstantMaturitySwap:
    def __init__(
        self, forward_swap_rate: float, swap_tenor_years: float, payment_frequency: float, volatility: float
    ) -> None:
        self.S0 = forward_swap_rate
        self.tenor = swap_tenor_years
        self.freq = payment_frequency
        self.volatility = volatility

    def _annuity(self, S: float) -> float:
        n = int(self.tenor * self.freq)
        return (1.0 / S) * (1.0 - 1.0 / (1.0 + S / self.freq) ** n)

    def convexity_adjustment(self, time_to_fixing: float) -> float:
        dS = 1e-5
        # Numerical derivatives
        A_plus = self._annuity(self.S0 + dS)
        A_minus = self._annuity(self.S0 - dS)
        A = self._annuity(self.S0)

        A_prime = (A_plus - A_minus) / (2 * dS)
        A_double_prime = (A_plus - 2 * A + A_minus) / (dS**2)

        # Standard convexity adjustment approximation
        ca = (
            -0.5
            * (self.S0**2)
            * (self.volatility**2)
            * time_to_fixing
            * (A_double_prime / A_prime)
        )
        return ca

    def adjusted_rate(self, time_to_fixing: float) -> float:
        return self.S0 + self.convexity_adjustment(time_to_fixing)
