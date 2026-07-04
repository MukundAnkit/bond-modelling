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

    def _drift(self, t: float, rates_t: np.ndarray, m_t: int) -> np.ndarray:
        # Calculate drift under spot measure for all rates
        n_rates = len(self.forward_rates)
        drift = np.zeros(n_rates)
        delta_T = np.diff(self.tenors)
        for i in range(m_t, n_rates):
            d = 0.0
            for j in range(m_t, i + 1):
                tau = delta_T[j]
                rho_ij = self.correlation_matrix[i, j]
                vol_i = self.volatilities[i]
                vol_j = self.volatilities[j]
                L_j = rates_t[j]
                d += (tau * rho_ij * vol_i * vol_j * L_j) / (1 + tau * L_j)
            drift[i] = d
        return drift

    def simulate_spot_measure(self, dt: float, n_paths: int, method='pc') -> np.ndarray:
        """
        Simulate forward rates under the spot martingale measure.

        :param dt: Time step
        :param n_paths: Number of Monte Carlo paths
        :param method: 'euler' or 'pc' (Predictor-Corrector Hunter-Jäckel)
        :return: Simulated forward rates paths of shape (n_paths, n_steps+1, n_rates)
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

            for p in range(n_paths):
                # Calculate drift under spot measure
                drift_t = self._drift(t, rates[p, t_idx, :], m_t)
                
                # Predictor step
                L_pred = np.copy(rates[p, t_idx, :])
                for i in alive_indices:
                    L_pred[i] = rates[p, t_idx, i] * np.exp(
                        (drift_t[i] - 0.5 * self.volatilities[i] ** 2) * dt
                        + self.volatilities[i] * dW[p, i]
                    )

                if method == 'pc':
                    # Corrector step
                    drift_pred = self._drift(t + dt, L_pred, m_t)
                    drift_avg = 0.5 * (drift_t + drift_pred)
                    
                    for i in alive_indices:
                        rates[p, t_idx + 1, i] = rates[p, t_idx, i] * np.exp(
                            (drift_avg[i] - 0.5 * self.volatilities[i] ** 2) * dt
                            + self.volatilities[i] * dW[p, i]
                        )
                else:
                    rates[p, t_idx + 1, :] = L_pred

            # For rates that have expired, just copy the last valid value or set to 0
            for i in range(m_t):
                rates[:, t_idx + 1, i] = rates[:, t_idx, i]

        return rates


class ForwardMarketModel(LiborMarketModel):
    """
    Forward Market Model (FMM) based on backward-looking compounded RFRs.
    Structurally similar to LMM but models OIS forward rates.
    """
    pass


class SABRForwardMarketModel:
    def __init__(
        self,
        forward_rates: list[float],
        tenors: list[float],
        alpha: list[float],
        beta: list[float],
        rho: list[float],
        nu: list[float],
        correlation_matrix: list[list[float]],
    ) -> None:
        """
        SABR-LMM / SABR-FMM Model
        """
        self.forward_rates = np.array(forward_rates)
        self.tenors = np.array(tenors)
        self.alpha = np.array(alpha) # Initial vol
        self.beta = np.array(beta)   # CEV parameter
        self.rho = np.array(rho)     # Correlation between rate and its vol
        self.nu = np.array(nu)       # Vol of vol
        self.correlation_matrix = np.array(correlation_matrix)
        
        self.cholesky = np.linalg.cholesky(self.correlation_matrix)

    def _drift(self, t: float, rates_t: np.ndarray, alpha_t: np.ndarray, m_t: int) -> np.ndarray:
        n_rates = len(self.forward_rates)
        drift = np.zeros(n_rates)
        delta_T = np.diff(self.tenors)
        for i in range(m_t, n_rates):
            d = 0.0
            for j in range(m_t, i + 1):
                tau = delta_T[j]
                rho_ij = self.correlation_matrix[i, j]
                vol_i = alpha_t[i] * (rates_t[i] ** (self.beta[i] - 1.0)) if rates_t[i] > 0 else 0
                vol_j = alpha_t[j] * (rates_t[j] ** (self.beta[j] - 1.0)) if rates_t[j] > 0 else 0
                L_j = rates_t[j]
                d += (tau * rho_ij * vol_i * vol_j * L_j) / (1 + tau * L_j)
            drift[i] = d
        return drift

    def simulate_spot_measure(self, dt: float, n_paths: int) -> tuple[np.ndarray, np.ndarray]:
        n_rates = len(self.forward_rates)
        T = self.tenors[-2]
        n_steps = int(T / dt)

        rates = np.zeros((n_paths, n_steps + 1, n_rates))
        alphas = np.zeros((n_paths, n_steps + 1, n_rates))
        
        rates[:, 0, :] = self.forward_rates
        alphas[:, 0, :] = self.alpha

        for t_idx in range(n_steps):
            t = t_idx * dt
            
            # Brownian motions for rates
            Z = np.random.standard_normal((n_paths, n_rates))
            dW = np.dot(Z, self.cholesky.T) * np.sqrt(dt)
            
            # Brownian motions for volatilities (correlated with rates via self.rho)
            Z_vol = np.random.standard_normal((n_paths, n_rates))
            dZ = (self.rho * dW + np.sqrt(1 - self.rho**2) * Z_vol * np.sqrt(dt))

            alive_indices = np.where(self.tenors[:-1] > t)[0]
            if len(alive_indices) == 0:
                break
            
            m_t = alive_indices[0]
            
            for p in range(n_paths):
                rates_t = rates[p, t_idx, :]
                alphas_t = alphas[p, t_idx, :]
                
                drift_t = self._drift(t, rates_t, alphas_t, m_t)
                
                for i in alive_indices:
                    # Euler step for SABR vol
                    alphas[p, t_idx + 1, i] = alphas_t[i] * np.exp(
                        -0.5 * self.nu[i]**2 * dt + self.nu[i] * dZ[p, i]
                    )
                    
                    # Euler step for rate using CEV
                    vol_i = alphas_t[i] * (rates_t[i] ** (self.beta[i] - 1.0)) if rates_t[i] > 0 else 0
                    
                    rates[p, t_idx + 1, i] = rates_t[i] * np.exp(
                        (drift_t[i] - 0.5 * vol_i**2) * dt + vol_i * dW[p, i]
                    )

            for i in range(m_t):
                rates[:, t_idx + 1, i] = rates[:, t_idx, i]
                alphas[:, t_idx + 1, i] = alphas[:, t_idx, i]

        return rates, alphas
