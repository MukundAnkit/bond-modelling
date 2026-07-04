"""Structural Credit Models (Merton)."""

import math
from dataclasses import dataclass

import numpy as np
from scipy.stats import norm


def merton_distance_to_default(
    asset_value: float,
    debt_face_value: float,
    asset_volatility: float,
    risk_free_rate: float,
    time_to_maturity: float,
) -> float:
    """Calculate distance to default using the Merton model.

    Parameters
    ----------
    asset_value : float
        Current market value of firm's assets.
    debt_face_value : float
        Face value of debt.
    asset_volatility : float
        Volatility of firm's assets.
    risk_free_rate : float
        Risk-free interest rate (continuous).
    time_to_maturity : float
        Time to debt maturity in years.

    Returns
    -------
    float
        Distance to default.

    """
    return MertonModel(
        V=asset_value,
        D=debt_face_value,
        T=time_to_maturity,
        r=risk_free_rate,
        sigma_V=asset_volatility,
    ).distance_to_default()


def merton_probability_of_default(distance_to_default: float) -> float:
    """Calculate risk-neutral probability of default from distance to default.

    Parameters
    ----------
    distance_to_default : float
        Distance to default (DD).

    Returns
    -------
    float
        Risk-neutral probability of default.

    """
    return float(norm.cdf(-distance_to_default))


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


@dataclass
class MertonJumpDiffusionModel(MertonModel):
    """Merton (1976) Jump-Diffusion Credit Model.

    Models a firm's asset value process as a jump-diffusion (Brownian motion + Poisson jumps).

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
        Volatility of the continuous component of firm's asset value.
    lambda_j : float
        Expected number of jumps per year.
    mu_j : float
        Mean of the jump size in log returns.
    sigma_j : float
        Volatility of the jump size.

    """

    lambda_j: float = 0.0
    mu_j: float = 0.0
    sigma_j: float = 0.0

    def equity_value(self, n_terms: int = 50) -> float:
        """Calculate the market value of the firm's equity under Jump-Diffusion."""
        if self.lambda_j == 0.0:
            return super().equity_value()

        k = np.exp(self.mu_j + 0.5 * self.sigma_j**2) - 1.0
        lambda_prime = self.lambda_j * (1.0 + k)

        call_price = 0.0
        for n in range(n_terms):
            prob = np.exp(-lambda_prime * self.T) * (lambda_prime * self.T)**n / math.factorial(n)

            sigma_n = np.sqrt(self.sigma_V**2 + n * self.sigma_j**2 / self.T)
            r_n = self.r - self.lambda_j * k + n * (self.mu_j + 0.5 * self.sigma_j**2) / self.T

            d1 = (np.log(self.V / self.D) + (r_n + 0.5 * sigma_n**2) * self.T) / (sigma_n * np.sqrt(self.T))
            d2 = d1 - sigma_n * np.sqrt(self.T)

            bs_call = self.V * norm.cdf(d1) - self.D * np.exp(-r_n * self.T) * norm.cdf(d2)
            call_price += prob * bs_call

        return float(call_price)

