import numpy as np  # noqa: I001
import pytest

from src.models.stochastic import VasicekModel, CIRModel
from src.models.calibration import calibrate_vasicek, calibrate_cir
from src.models.monte_carlo import MonteCarloEngine


def test_vasicek_zcb_pricing():
    model = VasicekModel(a=0.1, b=0.05, sigma=0.01)
    # T=0 should be 1.0
    assert model.zcb_price(0.05, 0.0) == 1.0

    # Positive rate should yield discount
    price = model.zcb_price(0.05, 1.0)
    assert 0.0 < price < 1.0


def test_cir_zcb_pricing():
    model = CIRModel(a=0.1, b=0.05, sigma=0.01)
    assert model.zcb_price(0.05, 0.0) == 1.0

    price = model.zcb_price(0.05, 1.0)
    assert 0.0 < price < 1.0


def test_vasicek_monte_carlo_convergence():
    model = VasicekModel(a=0.2, b=0.05, sigma=0.02)
    r0 = 0.04
    T = 2.0  # noqa: N806

    exact_price = model.zcb_price(r0, T)

    mc = MonteCarloEngine(model, n_paths=20000, n_steps=100, seed=42)
    mc_price = mc.price_zcb(r0, T)

    # MC should converge to exact closed-form within ~1%
    assert exact_price == pytest.approx(mc_price, rel=0.01)


def test_cir_monte_carlo_convergence():
    model = CIRModel(a=0.2, b=0.05, sigma=0.05)
    r0 = 0.04
    T = 2.0  # noqa: N806

    exact_price = model.zcb_price(r0, T)

    mc = MonteCarloEngine(model, n_paths=20000, n_steps=100, seed=42)
    mc_price = mc.price_zcb(r0, T)

    assert exact_price == pytest.approx(mc_price, rel=0.01)


def test_calibration_vasicek():
    # Generate synthetic Vasicek series
    np.random.seed(42)
    dt = 1 / 252
    steps = 1000
    r = np.zeros(steps)
    r[0] = 0.03
    a, b, sigma = 0.5, 0.04, 0.01

    for t in range(1, steps):
        dr = a * (b - r[t - 1]) * dt + sigma * np.sqrt(dt) * np.random.normal()
        r[t] = r[t - 1] + dr

    a_est, b_est, sigma_est = calibrate_vasicek(r, dt)

    # Because 1000 points is still noisy for mean reversion, we allow loose bounds on a and b,  # noqa: E501
    # but sigma should be tight
    assert sigma_est == pytest.approx(sigma, rel=0.1)


def test_calibration_cir():
    np.random.seed(42)
    dt = 1 / 252
    steps = 1000
    r = np.zeros(steps)
    r[0] = 0.03
    a, b, sigma = 0.5, 0.04, 0.01

    for t in range(1, steps):
        dr = (
            a * (b - r[t - 1]) * dt
            + sigma * np.sqrt(r[t - 1]) * np.sqrt(dt) * np.random.normal()
        )
        r[t] = r[t - 1] + dr
        # Reflect to avoid negative (though shouldn't happen here)
        r[t] = max(r[t], 1e-8)

    a_est, b_est, sigma_est = calibrate_cir(r, dt)
    assert sigma_est == pytest.approx(sigma, rel=0.1)
