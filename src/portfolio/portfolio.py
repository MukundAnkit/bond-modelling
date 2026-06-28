"""Portfolio class to represent a collection of bond positions."""

import numpy as np

from src.curve.nelson_siegel import NelsonSiegelCurve
from src.portfolio.position import Position
from src.risk.key_rate_duration import key_rate_durations
from src.risk.stress import SCENARIOS, shocked_price_non_parallel


class Portfolio:
    """A portfolio containing multiple bond positions.

    Provides aggregation of market value, weights, duration, convexity,
    DV01, Key Rate Durations, and regulatory stress testing.

    """

    def __init__(self) -> None:
        """Initialize an empty bond portfolio."""
        self._positions: list[Position] = []

    @property
    def positions(self) -> list[Position]:
        """List of positions in the portfolio."""
        return self._positions

    def add_position(self, position: Position) -> None:
        """Add a position to the portfolio.

        Parameters
        ----------
        position : Position
            The position to add.

        """
        self._positions.append(position)

    def market_value(self, yield_curve: NelsonSiegelCurve) -> float:
        """Calculate the total market value of the portfolio.

        Parameters
        ----------
        yield_curve : NelsonSiegelCurve
            The yield curve to use for pricing.

        Returns
        -------
        float
            Total market value.

        """
        return sum(pos.market_value(yield_curve) for pos in self._positions)

    def weights(self, yield_curve: NelsonSiegelCurve) -> np.ndarray:
        """Calculate the market value weights of the positions.

        Parameters
        ----------
        yield_curve : NelsonSiegelCurve
            The yield curve to use for pricing.

        Returns
        -------
        np.ndarray
            1-D array of position weights.

        """
        total_mv = self.market_value(yield_curve)
        if total_mv <= 0:
            return np.zeros(len(self._positions))
        return np.array(
            [pos.market_value(yield_curve) / total_mv for pos in self._positions]
        )

    def duration(self, yield_curve: NelsonSiegelCurve) -> float:
        """Calculate the weighted Modified Duration of the portfolio.

        Parameters
        ----------
        yield_curve : NelsonSiegelCurve
            The yield curve to use for pricing.

        Returns
        -------
        float
            Portfolio Modified Duration.

        """
        w = self.weights(yield_curve)
        d = np.array([pos.duration(yield_curve) for pos in self._positions])
        return float(np.sum(w * d))

    def convexity(self, yield_curve: NelsonSiegelCurve) -> float:
        """Calculate the weighted Convexity of the portfolio.

        Parameters
        ----------
        yield_curve : NelsonSiegelCurve
            The yield curve to use for pricing.

        Returns
        -------
        float
            Portfolio Convexity.

        """
        w = self.weights(yield_curve)
        c = np.array([pos.convexity(yield_curve) for pos in self._positions])
        return float(np.sum(w * c))

    def dv01(self, yield_curve: NelsonSiegelCurve) -> float:
        """Calculate the aggregate DV01 of the portfolio.

        Parameters
        ----------
        yield_curve : NelsonSiegelCurve
            The yield curve to use for pricing.

        Returns
        -------
        float
            Portfolio aggregate DV01.

        """
        return sum(pos.dv01(yield_curve) for pos in self._positions)

    def key_rate_duration(
        self,
        yield_curve: NelsonSiegelCurve,
        tenors: np.ndarray,
    ) -> np.ndarray:
        """Calculate the aggregated portfolio Key Rate Durations (KRDs).

        Parameters
        ----------
        yield_curve : NelsonSiegelCurve
            The yield curve to use for pricing.
        tenors : np.ndarray
            The key rate tenors (in years) to compute durations for.

        Returns
        -------
        np.ndarray
            The portfolio-level Key Rate Duration vector.

        """
        w = self.weights(yield_curve)
        portfolio_krd = np.zeros(len(tenors))

        for idx, pos in enumerate(self._positions):
            y = float(yield_curve.yield_rate(pos.bond.maturity))
            krd_dict = key_rate_durations(pos.bond, y, key_rates=tenors.tolist())
            pos_krd = np.array([krd_dict.get(t, 0.0) for t in tenors])
            portfolio_krd += w[idx] * pos_krd

        return portfolio_krd

    def stress_pnl(self, base_curve: NelsonSiegelCurve, scenario: str) -> float:
        """Calculate estimated portfolio P&L under a Basel IRBB scenario.

        Parameters
        ----------
        base_curve : NelsonSiegelCurve
            The base yield curve before the stress shock.
        scenario : str
            The name of the Basel IRBB scenario (e.g. ``"steepener"``).

        Returns
        -------
        float
            The total portfolio P&L.

        """
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario}")

        key_rates = [0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0]
        shocks = SCENARIOS[scenario](key_rates)
        total_pnl = 0.0

        for pos in self._positions:
            y_base = float(base_curve.yield_rate(pos.bond.maturity))
            p_base = pos.market_value(base_curve) / pos.quantity
            p_shocked = shocked_price_non_parallel(pos.bond, y_base, key_rates, shocks)
            total_pnl += pos.quantity * (p_shocked - p_base)

        return total_pnl
