"""Global Multi-Curve Solver for simultaneous curve calibration."""

import numpy as np

from src.bootstrap.interpolate import interpolate_df
from src.utils.math import newton_raphson_multi


class MultiCurveSolver:
    """Solves for multiple curves simultaneously (e.g. OIS discounting + Forward curves).

    This is an idealized implementation of a global solver that finds the zero rates
    for both a discount curve and a forward curve simultaneously such that all
    calibration instruments are priced exactly at par.
    """

    def __init__(
        self,
        ois_maturities: np.ndarray,
        ois_rates: np.ndarray,
        irs_maturities: np.ndarray,
        irs_rates: np.ndarray,
    ) -> None:
        """Initialize the multi-curve solver.

        Parameters
        ----------
        ois_maturities : np.ndarray
            Maturities of OIS instruments (years).
        ois_rates : np.ndarray
            Par rates for OIS instruments (decimal).
        irs_maturities : np.ndarray
            Maturities of IRS instruments (years) linked to a forward curve (e.g., 6M LIBOR).
        irs_rates : np.ndarray
            Par rates for IRS instruments (decimal).

        """
        self.ois_maturities = np.asarray(ois_maturities, dtype=np.float64)
        self.ois_rates = np.asarray(ois_rates, dtype=np.float64)
        self.irs_maturities = np.asarray(irs_maturities, dtype=np.float64)
        self.irs_rates = np.asarray(irs_rates, dtype=np.float64)

        self.n_ois = len(self.ois_maturities)
        self.n_irs = len(self.irs_maturities)

    def _pricing_error(self, x: np.ndarray) -> np.ndarray:
        """Calculate the pricing error for all instruments given curve zero rates.

        x = [ois_zero_rates..., irs_zero_rates...]
        """
        ois_zeros = x[: self.n_ois]
        irs_zeros = x[self.n_ois :]

        errors = np.zeros(self.n_ois + self.n_irs)

        # OIS Instruments (Discounted with OIS curve)
        for i in range(self.n_ois):
            T = self.ois_maturities[i]
            rate = self.ois_rates[i]

            # Simplified Swap pricing: Par rate = (1 - P(0, T)) / sum(P(0, t))
            # Error = 1 - P(0, T) - rate * sum_{k=1}^T P(0, k)
            n_periods = int(round(T * 1))  # Annual freq for simplicity
            sum_df = 0.0
            for k in range(1, n_periods + 1):
                df = interpolate_df(float(k), self.ois_maturities, ois_zeros)
                sum_df += df

            df_T = interpolate_df(T, self.ois_maturities, ois_zeros)
            errors[i] = (1.0 - df_T) - rate * sum_df

        # IRS Instruments (Cashflows from Forward curve, Discounted by OIS curve)
        for j in range(self.n_irs):
            T = self.irs_maturities[j]
            rate = self.irs_rates[j]

            n_periods = int(round(T * 2))  # Semi-annual freq for forward curve
            dt = 0.5

            pv_fixed = 0.0
            pv_float = 0.0

            for k in range(1, n_periods + 1):
                t = k * dt
                # Discount with OIS
                df_ois = interpolate_df(t, self.ois_maturities, ois_zeros)
                pv_fixed += rate * dt * df_ois

                # Forward rate implied from Forward curve
                if k == 1:
                    df_fwd_prev = 1.0
                else:
                    df_fwd_prev = interpolate_df(t - dt, self.irs_maturities, irs_zeros)
                df_fwd = interpolate_df(t, self.irs_maturities, irs_zeros)

                # Simple forward rate F = (P_{prev}/P_{curr} - 1) / dt
                fwd_rate = (df_fwd_prev / df_fwd - 1.0) / dt if df_fwd > 0 else 0.0

                pv_float += fwd_rate * dt * df_ois

            errors[self.n_ois + j] = pv_float - pv_fixed

        return errors

    def solve(self) -> tuple[np.ndarray, np.ndarray]:
        """Solve for both curves simultaneously.

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            Tuple containing (ois_zero_rates, irs_zero_rates).

        """
        # Initial guess: flat curves based on the last instrument rate
        guess_ois = np.full(self.n_ois, 0.02)
        guess_irs = np.full(self.n_irs, 0.03)
        guess = np.concatenate([guess_ois, guess_irs])

        # Use multivariate Newton-Raphson to find roots
        solution = newton_raphson_multi(self._pricing_error, guess)

        return solution[: self.n_ois], solution[self.n_ois :]
