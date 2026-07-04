# ruff: noqa
import numpy as np
from src.exotics.lmm import LiborMarketModel, ForwardMarketModel, SABRForwardMarketModel


def test_lmm_initialization():
    forward_rates = [0.02, 0.025, 0.03]
    tenors = [0.5, 1.0, 1.5, 2.0]
    volatilities = [0.15, 0.18, 0.20]
    correlation_matrix = [[1.0, 0.9, 0.8], [0.9, 1.0, 0.9], [0.8, 0.9, 1.0]]
    lmm = LiborMarketModel(forward_rates, tenors, volatilities, correlation_matrix)
    assert np.allclose(lmm.forward_rates, forward_rates)


def test_lmm_simulation_pc():
    forward_rates = [0.02, 0.025, 0.03]
    tenors = [0.5, 1.0, 1.5, 2.0]
    volatilities = [0.15, 0.18, 0.20]
    correlation_matrix = [[1.0, 0.9, 0.8], [0.9, 1.0, 0.9], [0.8, 0.9, 1.0]]
    lmm = LiborMarketModel(forward_rates, tenors, volatilities, correlation_matrix)

    np.random.seed(42)
    paths_pc = lmm.simulate_spot_measure(dt=0.25, n_paths=100, method="pc")

    assert paths_pc.shape == (100, 7, 3)
    assert not np.isnan(paths_pc).any()
    assert np.mean(paths_pc[:, -1, :]) > 0

    np.random.seed(42)
    paths_euler = lmm.simulate_spot_measure(dt=0.25, n_paths=100, method="euler")
    assert not np.isnan(paths_euler).any()


def test_fmm_initialization():
    fmm = ForwardMarketModel([0.02], [0.5, 1.0], [0.2], [[1.0]])
    assert fmm.forward_rates[0] == 0.02


def test_sabr_fmm_simulation():
    forward_rates = [0.02, 0.025]
    tenors = [0.5, 1.0, 1.5]
    alpha = [0.1, 0.1]
    beta = [0.5, 0.5]
    rho = [-0.3, -0.3]
    nu = [0.4, 0.4]
    correlation_matrix = [[1.0, 0.8], [0.8, 1.0]]

    sabr = SABRForwardMarketModel(
        forward_rates, tenors, alpha, beta, rho, nu, correlation_matrix
    )

    np.random.seed(42)
    rates, alphas = sabr.simulate_spot_measure(dt=0.25, n_paths=50)

    assert rates.shape == (50, 5, 2)
    assert alphas.shape == (50, 5, 2)
    assert not np.isnan(rates).any()
    assert not np.isnan(alphas).any()
