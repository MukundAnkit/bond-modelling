# ruff: noqa
import numpy as np
from src.exotics.lmm import LiborMarketModel


def test_lmm_initialization():
    forward_rates = [0.02, 0.025, 0.03]
    tenors = [0.5, 1.0, 1.5, 2.0]
    volatilities = [0.15, 0.18, 0.20]
    correlation_matrix = [[1.0, 0.9, 0.8], [0.9, 1.0, 0.9], [0.8, 0.9, 1.0]]
    lmm = LiborMarketModel(forward_rates, tenors, volatilities, correlation_matrix)
    assert np.allclose(lmm.forward_rates, forward_rates)


def test_lmm_simulation():
    forward_rates = [0.02, 0.025, 0.03]
    tenors = [0.5, 1.0, 1.5, 2.0]
    volatilities = [0.15, 0.18, 0.20]
    correlation_matrix = [[1.0, 0.9, 0.8], [0.9, 1.0, 0.9], [0.8, 0.9, 1.0]]
    lmm = LiborMarketModel(forward_rates, tenors, volatilities, correlation_matrix)

    np.random.seed(42)
    paths = lmm.simulate_spot_measure(dt=0.25, n_paths=100)

    assert paths.shape == (100, 7, 3)  # dt=0.25 up to T=1.5 -> 6 steps + 1 initial
    assert not np.isnan(paths).any()
    assert np.mean(paths[:, -1, :]) > 0
