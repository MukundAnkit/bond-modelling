"""Nelson-Siegel parametric yield curve modeling and optimization."""

import numpy as np
from typing import Any
from scipy.optimize import minimize


class NelsonSiegelCurve:
    """A continuous yield curve represented by the Nelson-Siegel parametric model.

    The Nelson-Siegel model defines the yield to maturity y(t) at time t as:
    y(t) = beta0 + beta1 * ((1 - e^{-t/tau}) / (t/tau)) +
           beta2 * ((1 - e^{-t/tau}) / (t/tau) - e^{-t/tau})

    Parameters
    ----------
    beta0 : float
        Level parameter (long-term yield).
    beta1 : float
        Slope parameter (short-term component).
    beta2 : float
        Curvature parameter (medium-term component).
    tau : float
        Decay parameter (governing the location of the hump/curvature peak).

    """

    def __init__(
        self,
        beta0: float,
        beta1: float,
        beta2: float,
        tau: float,
    ) -> None:
        """Initialize Nelson-Siegel curve parameters.

        Parameters
        ----------
        beta0 : float
            Level parameter (long-term yield).
        beta1 : float
            Slope parameter (short-term component).
        beta2 : float
            Curvature parameter (medium-term component).
        tau : float
            Decay parameter (governing the location of the hump).

        """
        self._beta0 = float(beta0)
        self._beta1 = float(beta1)
        self._beta2 = float(beta2)
        self._tau = float(tau)

        if self._beta0 <= 0:
            raise ValueError("beta0 (level) must be strictly positive")
        if self._tau <= 0:
            raise ValueError("tau (decay) must be strictly positive")

    @property
    def beta0(self) -> float:
        """Level parameter (beta0)."""
        return self._beta0

    @property
    def beta1(self) -> float:
        """Slope parameter (beta1)."""
        return self._beta1

    @property
    def beta2(self) -> float:
        """Curvature parameter (beta2)."""
        return self._beta2

    @property
    def tau(self) -> float:
        """Decay parameter (tau)."""
        return self._tau

    @property
    def level(self) -> float:
        """Level parameter alias (beta0)."""
        return self._beta0

    @property
    def slope(self) -> float:
        """Slope parameter alias (beta1)."""
        return self._beta1

    @property
    def curvature(self) -> float:
        """Curvature parameter alias (beta2)."""
        return self._beta2

    @property
    def decay(self) -> float:
        """Decay parameter alias (tau)."""
        return self._tau

    def yield_rate(self, t: float | np.ndarray) -> float | np.ndarray:
        """Evaluate the Nelson-Siegel yield rate(s) for maturity t.

        Parameters
        ----------
        t : float or np.ndarray
            Time(s) to maturity in years. Must be non-negative.

        Returns
        -------
        float or np.ndarray
            The continuous yield rate(s) at t.

        """
        t_arr = np.asarray(t, dtype=np.float64)
        if np.any(t_arr < 0):
            raise ValueError("Time to maturity t must be non-negative")

        # Avoid division by zero at t=0
        # As t -> 0, the first term multiplier ((1 - e^{-t/tau}) / (t/tau)) -> 1
        # The second term multiplier ((1 - e^{-t/tau}) / (t/tau) - e^{-t/tau}) -> 0
        eps = 1e-12
        t_safe = np.where(t_arr < eps, eps, t_arr)

        # Compute components using vectorized numpy
        factor = (1.0 - np.exp(-t_safe / self._tau)) / (t_safe / self._tau)
        term1 = factor
        term2 = factor - np.exp(-t_safe / self._tau)

        # Replace t < eps values with their analytical limits
        term1 = np.where(t_arr < eps, 1.0, term1)
        term2 = np.where(t_arr < eps, 0.0, term2)

        y = self._beta0 + self._beta1 * term1 + self._beta2 * term2

        # If the input was a scalar (not an array), return a float
        if not isinstance(t, np.ndarray) or t.ndim == 0:
            return float(y)
        return y

    def __call__(self, t: float | np.ndarray) -> float | np.ndarray:
        """Evaluate the Nelson-Siegel yield rate(s) for maturity t.

        Convenience wrapper for ``yield_rate``.

        """
        return self.yield_rate(t)

    def sse(self, maturities: np.ndarray, spot_rates: np.ndarray) -> float:
        """Calculate the Sum of Squared Errors (SSE) for given spot rates.

        Parameters
        ----------
        maturities : np.ndarray
            1-D array of observed maturities in years.
        spot_rates : np.ndarray
            1-D array of observed spot rates as decimals.

        Returns
        -------
        float
            The Sum of Squared Errors.

        """
        m_arr = np.asarray(maturities, dtype=np.float64)
        s_arr = np.asarray(spot_rates, dtype=np.float64)
        predicted = self.yield_rate(m_arr)
        return float(np.sum((predicted - s_arr) ** 2))

    @classmethod
    def fit(
        cls,
        maturities: np.ndarray,
        spot_rates: np.ndarray,
        init_guess: list[float] | None = None,
        method: str = "Nelder-Mead",
        **kwargs: Any,
    ) -> "NelsonSiegelCurve":
        """Fit a Nelson-Siegel curve to discrete spot rates.

        Parameters
        ----------
        maturities : np.ndarray
            1-D array of observed maturities in years. Must be positive.
        spot_rates : np.ndarray
            1-D array of observed spot rates as decimals.
        init_guess : list of float, optional
            Initial guess for the optimization parameters: [beta0, beta1, beta2, tau].
            If None, a heuristic multi-start guess will be generated.
        method : str, optional
            The optimization method. Default is ``"Nelder-Mead"``.
        **kwargs : dict
            Additional keyword arguments passed to ``scipy.optimize.minimize``.

        Returns
        -------
        NelsonSiegelCurve
            The fitted NelsonSiegelCurve object.

        Raises
        ------
        ValueError
            If inputs fail validation (e.g. empty arrays, mismatched lengths,
            non-positive maturities).
        RuntimeError
            If the optimization solver fails to converge.

        """
        m_arr = np.asarray(maturities, dtype=np.float64)
        s_arr = np.asarray(spot_rates, dtype=np.float64)

        if len(m_arr) != len(s_arr):
            raise ValueError("maturities and spot_rates must have the same length")
        if len(m_arr) == 0:
            raise ValueError("maturities and spot_rates cannot be empty")
        if np.any(m_arr <= 0):
            raise ValueError("maturities must be strictly positive")

        # Constraints / Bounds
        # beta0 > 0 -> beta0 >= 1e-6
        # tau > 0 -> tau >= 1e-6
        # beta1 and beta2 are unconstrained
        bounds = [
            (1e-6, None),  # beta0 bounds
            (None, None),  # beta1 bounds
            (None, None),  # beta2 bounds
            (1e-6, None),  # tau bounds
        ]

        # Objective function: minimize SSE
        def objective(params: list[float]) -> float:
            b0, b1, b2, t_val = params
            # To prevent optimizer from hitting float errors at bound boundaries
            if b0 <= 0 or t_val <= 0:
                return 1e12

            # Vectorized yield computation:
            eps = 1e-12
            m_safe = np.where(m_arr < eps, eps, m_arr)
            factor = (1.0 - np.exp(-m_safe / t_val)) / (m_safe / t_val)
            term1 = np.where(m_arr < eps, 1.0, factor)
            term2 = np.where(m_arr < eps, 0.0, factor - np.exp(-m_safe / t_val))

            predicted = b0 + b1 * term1 + b2 * term2
            return float(np.sum((predicted - s_arr) ** 2))

        # Perform optimization
        if init_guess is not None:
            if len(init_guess) != 4:
                raise ValueError("init_guess must have length 4")
            # Ensure initial guess is strictly within bounds
            x0 = [
                max(1e-6, float(init_guess[0])),
                float(init_guess[1]),
                float(init_guess[2]),
                max(1e-6, float(init_guess[3])),
            ]
            res = minimize(
                objective,
                x0=x0,
                method=method,
                bounds=bounds,
                **kwargs,
            )
            if not res.success:
                raise RuntimeError(
                    f"Nelson-Siegel curve optimization failed: {res.message}"
                )
            best_x = res.x
        else:
            # Multi-start heuristic to avoid local minima
            # beta0: long-term rate (use longest maturity rate, clipped to lower bound)
            beta0_init = max(1e-6, float(s_arr[-1]))
            # beta0 + beta1: short-term rate (use shortest maturity rate)
            beta1_init = float(s_arr[0] - beta0_init)
            beta2_init = 0.0

            # Candidate values for tau to start optimization
            tau_guesses = [0.5, 1.0, 2.0, 5.0, 10.0]
            best_fun = 1e12
            best_x = None
            opt_error_msg = ""

            for tau_guess in tau_guesses:
                x0 = [beta0_init, beta1_init, beta2_init, tau_guess]
                res = minimize(
                    objective,
                    x0=x0,
                    method=method,
                    bounds=bounds,
                    **kwargs,
                )
                if res.success and res.fun < best_fun:
                    best_fun = res.fun
                    best_x = res.x
                elif not res.success:
                    opt_error_msg = res.message

            if best_x is None:
                raise RuntimeError(
                    "Nelson-Siegel curve optimization failed to converge: "
                    f"{opt_error_msg}"
                )

        return cls(
            beta0=best_x[0],
            beta1=best_x[1],
            beta2=best_x[2],
            tau=best_x[3],
        )
