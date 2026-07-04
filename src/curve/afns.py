"""Arbitrage-Free Nelson-Siegel (AFNS) yield curve modeling."""

from typing import Any

import numpy as np
from scipy.optimize import minimize

from src.curve.nelson_siegel import NelsonSiegelCurve


class ArbitrageFreeNelsonSiegel(NelsonSiegelCurve):
    """Arbitrage-Free Nelson-Siegel (AFNS) parametric yield curve model.

    Extends the standard Nelson-Siegel model by introducing a convexity adjustment
    term that ensures the model is arbitrage-free under a dynamic term structure
    setting (Christensen, Diebold, and Rudebusch, 2011).
    
    The yield is given by:
    y(t) = beta0 + beta1 * ((1 - e^{-t/tau}) / (t/tau)) +
           beta2 * ((1 - e^{-t/tau}) / (t/tau) - e^{-t/tau}) - convexity_adjustment(t)
    """

    def __init__(
        self,
        beta0: float,
        beta1: float,
        beta2: float,
        tau: float,
        sigma: float,
    ) -> None:
        """Initialize AFNS curve parameters.

        Parameters
        ----------
        beta0 : float
            Level parameter.
        beta1 : float
            Slope parameter.
        beta2 : float
            Curvature parameter.
        tau : float
            Decay parameter (governing the location of the hump).
        sigma : float
            Volatility parameter used for the convexity adjustment.
        """
        super().__init__(beta0, beta1, beta2, tau)
        self._sigma = float(sigma)
        if self._sigma < 0:
            raise ValueError("sigma (volatility) must be non-negative")

    @property
    def sigma(self) -> float:
        """Volatility parameter."""
        return self._sigma

    def convexity_adjustment(self, t: float | np.ndarray) -> float | np.ndarray:
        """Calculate the AFNS convexity adjustment term for maturity t.

        Parameters
        ----------
        t : float or np.ndarray
            Time to maturity in years.

        Returns
        -------
        float or np.ndarray
            The convexity adjustment subtracted from the yield.
        """
        t_arr = np.asarray(t, dtype=np.float64)
        eps = 1e-12
        t_safe = np.where(t_arr < eps, eps, t_arr)

        lambda_ = 1.0 / self._tau
        
        # Simplified standard independent factor AFNS convexity adjustment
        # C(t) = sigma^2 * (t^2 / 6 + ... )
        # Using a generalized approximation for demonstration:
        term = (self._sigma ** 2) * (t_safe ** 2) / 6.0
        
        adj = np.where(t_arr < eps, 0.0, term)
        if not isinstance(t, np.ndarray) or t.ndim == 0:
            return float(adj)
        return adj

    def yield_rate(self, t: float | np.ndarray) -> float | np.ndarray:
        """Evaluate the AFNS yield rate(s) for maturity t."""
        base_yield = super().yield_rate(t)
        adj = self.convexity_adjustment(t)
        return base_yield - adj

    @classmethod
    def fit(
        cls,
        maturities: np.ndarray,
        spot_rates: np.ndarray,
        init_guess: list[float] | None = None,
        method: str = "Nelder-Mead",
        **kwargs: Any,
    ) -> "ArbitrageFreeNelsonSiegel":
        """Fit an AFNS curve to discrete spot rates."""
        m_arr = np.asarray(maturities, dtype=np.float64)
        s_arr = np.asarray(spot_rates, dtype=np.float64)

        bounds = [
            (1e-6, None),  # beta0
            (None, None),  # beta1
            (None, None),  # beta2
            (1e-6, None),  # tau
            (1e-6, 0.5),   # sigma (reasonable vol bound)
        ]

        def objective(params: list[float]) -> float:
            b0, b1, b2, t_val, sig = params
            if b0 <= 0 or t_val <= 0 or sig < 0:
                return 1e12

            # Base NS
            eps = 1e-12
            m_safe = np.where(m_arr < eps, eps, m_arr)
            factor = (1.0 - np.exp(-m_safe / t_val)) / (m_safe / t_val)
            term1 = np.where(m_arr < eps, 1.0, factor)
            term2 = np.where(m_arr < eps, 0.0, factor - np.exp(-m_safe / t_val))
            
            base_yield = b0 + b1 * term1 + b2 * term2
            
            # Convexity adj
            adj = np.where(m_arr < eps, 0.0, (sig ** 2) * (m_safe ** 2) / 6.0)
            
            predicted = base_yield - adj
            return float(np.sum((predicted - s_arr) ** 2))

        if init_guess is None:
            # Multi-start heuristic
            beta0_init = max(1e-6, float(s_arr[-1]))
            beta1_init = float(s_arr[0] - beta0_init)
            
            best_fun = 1e12
            best_x = None
            for tau_g in [0.5, 2.0, 5.0]:
                for sig_g in [0.01, 0.05]:
                    x0 = [beta0_init, beta1_init, 0.0, tau_g, sig_g]
                    res = minimize(objective, x0=x0, method=method, bounds=bounds, **kwargs)
                    if res.success and res.fun < best_fun:
                        best_fun = res.fun
                        best_x = res.x
            if best_x is None:
                raise RuntimeError("AFNS optimization failed to converge.")
        else:
            x0 = init_guess
            res = minimize(objective, x0=x0, method=method, bounds=bounds, **kwargs)
            if not res.success:
                raise RuntimeError(f"AFNS optimization failed: {res.message}")
            best_x = res.x

        return cls(beta0=best_x[0], beta1=best_x[1], beta2=best_x[2], tau=best_x[3], sigma=best_x[4])
