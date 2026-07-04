import typing

import numpy as np


class MonteCarloEngine:
    """Monte Carlo simulation engine for interest rate paths."""

    def __init__(
        self,
        model: typing.Any,
        n_paths: int = 10000,
        n_steps: int = 252,
        seed: int | None = None,
    ):
        self.model = model
        self.n_paths = n_paths
        self.n_steps = n_steps
        self.seed = seed

    def simulate_paths(self, r0: float | tuple[float, float], T: float) -> np.ndarray:
        """Simulate interest rate paths using Euler-Maruyama discretization.

        Args:
            r0: Initial short rate (or tuple (x0, y0) for 2-factor models).
            T: Time horizon in years.

        Returns:
            np.ndarray of shape (n_steps + 1, n_paths) containing simulated rates.

        """
        if self.seed is not None:
            np.random.seed(self.seed)

        dt = T / self.n_steps
        paths = np.zeros((self.n_steps + 1, self.n_paths))

        model_name = (
            self.model.__class__.__name__ if hasattr(self.model, "__class__") else ""
        )

        if model_name == "HullWhite2FModel":
            x0, y0 = r0 if isinstance(r0, tuple) else (r0, 0.0)
            paths_x = np.zeros((self.n_steps + 1, self.n_paths))
            paths_y = np.zeros((self.n_steps + 1, self.n_paths))
            paths_x[0] = x0
            paths_y[0] = y0
            paths[0] = x0 + y0 + self.model.phi(0.0)
        else:
            paths[0] = r0

        sqrt_dt = np.sqrt(dt)

        for t in range(1, self.n_steps + 1):
            curr_time = (t - 1) * dt

            if model_name == "HullWhite2FModel":
                Z1 = np.random.normal(0, 1, self.n_paths)
                Z2 = np.random.normal(0, 1, self.n_paths)

                # Correlated brownian motions
                dW1 = Z1 * sqrt_dt
                dW2 = (
                    self.model.rho * Z1 + np.sqrt(1 - self.model.rho**2) * Z2
                ) * sqrt_dt

                x_prev = paths_x[t - 1]
                y_prev = paths_y[t - 1]

                dx = -self.model.a * x_prev * dt + self.model.sigma1 * dW1
                dy = -self.model.b * y_prev * dt + self.model.sigma2 * dW2

                paths_x[t] = x_prev + dx
                paths_y[t] = y_prev + dy
                paths[t] = paths_x[t] + paths_y[t] + self.model.phi(curr_time + dt)
                continue

            dW = np.random.normal(0, 1, self.n_paths) * sqrt_dt
            r_prev = paths[t - 1]

            if model_name == "CIRModel":
                drift = self.model.a * (self.model.b - r_prev) * dt
                diffusion = self.model.sigma * np.sqrt(np.abs(r_prev)) * dW
                paths[t] = r_prev + drift + diffusion
            elif model_name == "ShiftedCIRModel":
                x_prev = r_prev - self.model.shift
                drift = self.model.a * (self.model.b - x_prev) * dt
                diffusion = self.model.sigma * np.sqrt(np.abs(x_prev)) * dW
                paths[t] = (x_prev + drift + diffusion) + self.model.shift
            elif model_name == "HullWhite1FModel":
                drift = (self.model.theta(curr_time) - self.model.a * r_prev) * dt
                diffusion = self.model.sigma * dW
                paths[t] = r_prev + drift + diffusion
            elif model_name == "ShiftedLognormalModel":
                x_prev = r_prev - self.model.shift
                x_prev_safe = np.maximum(x_prev, 1e-8)  # prevent log of <= 0
                drift = (
                    (self.model.theta - self.model.a * np.log(x_prev_safe))
                    * x_prev_safe
                    * dt
                )
                diffusion = self.model.sigma * x_prev_safe * dW
                paths[t] = (x_prev_safe + drift + diffusion) + self.model.shift
            else:
                # Default Vasicek
                drift = self.model.a * (self.model.b - r_prev) * dt
                diffusion = self.model.sigma * dW
                paths[t] = r_prev + drift + diffusion

        return paths

    def price_zcb(self, r0: float | tuple[float, float], T: float) -> float:
        """Price a Zero-Coupon Bond using Monte Carlo simulation."""
        if T == 0:
            return 1.0

        paths = self.simulate_paths(r0, T)
        dt = T / self.n_steps

        # Integral approximation using Riemann sum
        integral = np.sum(paths[:-1], axis=0) * dt

        discount_factors = np.exp(-integral)
        return float(np.mean(discount_factors))
