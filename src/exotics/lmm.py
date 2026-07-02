# ruff: noqa
# mypy: ignore-errors
import numpy as np


class LiborMarketModel:
    def __init__(
        self,
        forward_rates: list[float],
        tenors: list[float],
        volatilities: list[float],
        correlation_matrix: list[list[float]],
    ) -> None:
        """
        Initialize the LIBOR Market Model (BGM).

        :param forward_rates: Initial forward rates L_i(0)
        :param tenors: Time points T_i
        :param volatilities: Volatility functions or constant volatilities for each rate
        :param correlation_matrix: Correlation matrix between the forward rates
        """
        self.forward_rates = np.array(forward_rates)
        self.tenors = np.array(tenors)
        self.volatilities = np.array(volatilities)
        self.correlation_matrix = np.array(correlation_matrix)

        assert len(self.forward_rates) == len(self.tenors) - 1
        assert len(self.volatilities) == len(self.forward_rates)
        assert self.correlation_matrix.shape == (
            len(self.forward_rates),
            len(self.forward_rates),
        )

        # Cholesky decomposition of correlation matrix
        self.cholesky = np.linalg.cholesky(self.correlation_matrix)

    def simulate_spot_measure(self, dt: float, n_paths: int) -> np.ndarray:
        """
        Simulate forward rates under the spot martingale measure using Euler discretization.

        :param dt: Time step
        :param n_paths: Number of Monte Carlo paths
        :return: Simulated forward rates paths of shape (n_paths, n_steps, n_rates)
        """
        n_rates = len(self.forward_rates)
        T = self.tenors[-2]  # Last time to simulate to
        n_steps = int(T / dt)

        rates = np.zeros((n_paths, n_steps + 1, n_rates))
        rates[:, 0, :] = self.forward_rates

        delta_T = np.diff(self.tenors)

        for t_idx in range(n_steps):
            t = t_idx * dt

            # Generate correlated Brownian increments
            Z = np.random.standard_normal((n_paths, n_rates))
            dW = np.dot(Z, self.cholesky.T) * np.sqrt(dt)

            # Identify which rates are still alive (T_i > t)
            alive_indices = np.where(self.tenors[:-1] > t)[0]
            if len(alive_indices) == 0:
                break

            m_t = alive_indices[0]  # Index of the next maturity

            for i in alive_indices:
                # Calculate drift under spot measure
                drift = 0.0
                for j in range(m_t, i + 1):
                    tau = delta_T[j]
                    rho_ij = self.correlation_matrix[i, j]
                    vol_i = self.volatilities[i]
                    vol_j = self.volatilities[j]
                    L_j = rates[:, t_idx, j]
                    drift += (tau * rho_ij * vol_i * vol_j * L_j) / (1 + tau * L_j)

                # Euler step for L_i
                rates[:, t_idx + 1, i] = rates[:, t_idx, i] * np.exp(
                    (drift - 0.5 * self.volatilities[i] ** 2) * dt
                    + self.volatilities[i] * dW[:, i]
                )

            # For rates that have expired, just copy the last valid value or set to 0
            for i in range(m_t):
                rates[:, t_idx + 1, i] = rates[:, t_idx, i]

        return rates
