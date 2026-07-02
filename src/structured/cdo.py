# ruff: noqa
# mypy: ignore-errors
import numpy as np
from typing import List
from .tranche import Tranche
from .copula import Copula, default_times_from_copula


class SyntheticCDO:
    def __init__(
        self,
        tranches: List[Tranche],
        hazard_rates: np.ndarray,
        recovery_rate: float = 0.4,
    ):
        self.tranches = tranches
        self.hazard_rates = hazard_rates
        self.recovery_rate = recovery_rate
        self.n_credits = len(hazard_rates)

    def simulate_tranche_losses(
        self,
        copula: Copula,
        time_horizon: float,
        n_samples: int = 10000,
        seed: int | None = None,
    ) -> dict:
        u = copula.simulate(n_samples=n_samples, seed=seed)
        tau = default_times_from_copula(u, self.hazard_rates)
        defaults = tau <= time_horizon
        pool_loss_fraction = (
            np.sum(defaults, axis=1) * (1.0 - self.recovery_rate) / self.n_credits
        )

        results = {}
        for tranche in self.tranches:
            tranche_loss = tranche.calculate_loss(pool_loss_fraction)
            results[tranche.name] = {
                "expected_loss": np.mean(tranche_loss),
                "loss_std": np.std(tranche_loss),
                "loss_distribution": tranche_loss,
            }

        return results
