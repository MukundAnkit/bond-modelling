import typing  # noqa: D100, I001
import numpy as np  # noqa: D100


class MonteCarloEngine:
    """Monte Carlo simulation engine for interest rate paths."""

    def __init__(  # noqa: D107
        self,
        model: typing.Any,
        n_paths: int = 10000,
        n_steps: int = 252,
        seed: int | None = None,  # noqa: E501
    ):
        self.model = model
        self.n_paths = n_paths
        self.n_steps = n_steps
        self.seed = seed

    def simulate_paths(self, r0: float, T: float) -> np.ndarray:  # noqa: N803
        """Simulate interest rate paths using Euler-Maruyama discretization.

        Args:
            r0: Initial short rate.
            T: Time horizon in years.

        Returns:
            np.ndarray of shape (n_steps + 1, n_paths) containing simulated rates.
        """  # noqa: D413
        if self.seed is not None:
            np.random.seed(self.seed)

        dt = T / self.n_steps
        paths = np.zeros((self.n_steps + 1, self.n_paths))
        paths[0] = r0

        sqrt_dt = np.sqrt(dt)

        is_cir = (
            hasattr(self.model, "__class__")
            and self.model.__class__.__name__ == "CIRModel"
        )

        for t in range(1, self.n_steps + 1):
            dW = np.random.normal(0, 1, self.n_paths) * sqrt_dt  # noqa: N806
            r_prev = paths[t - 1]
            drift = self.model.a * (self.model.b - r_prev) * dt

            if is_cir:
                # Use absolute value for CIR to prevent domain errors (Full Truncation / Reflection scheme)  # noqa: E501
                diffusion = self.model.sigma * np.sqrt(np.abs(r_prev)) * dW
                # For strict Full Truncation: paths[t] = r_prev + drift + diffusion, and max(0, paths[t]) on next iter  # noqa: E501
                # Here we'll just allow it and take abs inside sqrt next step.
            else:
                diffusion = self.model.sigma * dW

            paths[t] = r_prev + drift + diffusion

        return paths

    def price_zcb(self, r0: float, T: float) -> float:  # noqa: N803
        """Price a Zero-Coupon Bond using Monte Carlo simulation.

        Computes expectation under the risk-neutral measure: E[exp(-integral_0^T r_t dt)]
        """  # noqa: E501
        if T == 0:
            return 1.0

        paths = self.simulate_paths(r0, T)
        dt = T / self.n_steps

        # Integral approximation using Riemann sum
        integral = np.sum(paths[:-1], axis=0) * dt

        discount_factors = np.exp(-integral)
        return float(np.mean(discount_factors))
