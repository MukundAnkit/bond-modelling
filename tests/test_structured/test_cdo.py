# ruff: noqa
import numpy as np
from src.structured.tranche import Tranche
from src.structured.copula import GaussianCopula
from src.structured.cdo import SyntheticCDO


def test_synthetic_cdo():
    n_credits = 10
    corr = np.eye(n_credits) * 0.5 + 0.5
    np.fill_diagonal(corr, 1.0)

    copula = GaussianCopula(corr)
    hazard_rates = np.ones(n_credits) * 0.05

    tranches = [Tranche(0.0, 0.1, "Equity"), Tranche(0.1, 0.3, "Mezzanine")]

    cdo = SyntheticCDO(tranches, hazard_rates, recovery_rate=0.4)
    results = cdo.simulate_tranche_losses(
        copula, time_horizon=5.0, n_samples=1000, seed=42
    )

    assert "Equity" in results
    assert "Mezzanine" in results
    assert results["Equity"]["expected_loss"] > results["Mezzanine"]["expected_loss"]
