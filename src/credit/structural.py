"""Structural Credit Models (Merton)."""

from dataclasses import dataclass

import numpy as np
from scipy.stats import norm


@dataclass
class MertonModel:
    """Merton (1974) Structural Credit Model.

    Models a firm's equity as a European Call option on its assets,
    where the strike price is the face value of the firm's zero-coupon debt.

    Parameters
    ----------
    V : float
        Current market value of the firm's assets.
    D : float
        Face value of the firm's zero-coupon debt.
    T : float
        Time to maturity of the debt in years.
    r : float
        Risk-free interest rate (continuous).
    sigma_V : float
        Volatility of the firm's asset value.

    """

    V: float  # noqa: N815
    D: float  # noqa: N815
    T: float  # noqa: N815
    r: float
    sigma_V: float  # noqa: N815

    def _d1(self) -> float:
        """Calculate the d1 parameter in Black-Scholes formula."""
        num = np.log(self.V / self.D) + (self.r + 0.5 * self.sigma_V**2) * self.T
        den = self.sigma_V * np.sqrt(self.T)
        return float(num / den)

    def _d2(self) -> float:
        """Calculate the d2 parameter in Black-Scholes formula."""
        return float(self._d1() - self.sigma_V * np.sqrt(self.T))

    def equity_value(self) -> float:
        """Calculate the market value of the firm's equity."""
        d1 = self._d1()
        d2 = self._d2()

        return float(
            self.V * norm.cdf(d1) - self.D * np.exp(-self.r * self.T) * norm.cdf(d2)
        )

    def debt_value(self) -> float:
        """Calculate the market value of the firm's debt.

        By the fundamental accounting equation, D = V - E.
        """
        return float(self.V - self.equity_value())

    def distance_to_default(self) -> float:
        """Calculate the distance to default (DD).

        DD is essentially d2 from the Black-Scholes formula.
        """
        return self._d2()

    def probability_of_default(self) -> float:
        """Calculate the risk-neutral probability of default (PD).

        PD = N(-d2) = N(-DD).
        """
        return float(norm.cdf(-self.distance_to_default()))

    def credit_spread(self) -> float:
        """Calculate the credit spread implied by the Merton model.

        Spread = - (1/T) * ln(Debt Value / Risk-Free Debt Value)
        """
        risk_free_debt = self.D * np.exp(-self.r * self.T)
        debt = self.debt_value()

        if debt <= 0:
            return float("inf")

        return float(-(1.0 / self.T) * np.log(debt / risk_free_debt))
