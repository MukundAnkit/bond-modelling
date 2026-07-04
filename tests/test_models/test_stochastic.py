import numpy as np
import pytest

from src.models.calibration import calibrate_cir, calibrate_vasicek
from src.models.monte_carlo import MonteCarloEngine
from src.models.stochastic import (
    CIRModel,
    HullWhite1FModel,
    HullWhite2FModel,
    ShiftedCIRModel,
    ShiftedLognormalModel,
    VasicekModel,
)


def test_vasicek_zcb_pricing():
    model = VasicekModel(a=0.1, b=0.05, sigma=0.01)
    assert model.zcb_price(0.05, 0.0) == 1.0
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
    T = 2.0

    exact_price = model.zcb_price(r0, T)
    mc = MonteCarloEngine(model, n_paths=20000, n_steps=100, seed=42)
    mc_price = mc.price_zcb(r0, T)
    assert exact_price == pytest.approx(mc_price, rel=0.01)


def test_cir_monte_carlo_convergence():
    model = CIRModel(a=0.2, b=0.05, sigma=0.05)
    r0 = 0.04
    T = 2.0

    exact_price = model.zcb_price(r0, T)
    mc = MonteCarloEngine(model, n_paths=20000, n_steps=100, seed=42)
    mc_price = mc.price_zcb(r0, T)
    assert exact_price == pytest.approx(mc_price, rel=0.01)


def test_hull_white_1f_zcb_pricing():
    # When theta is constant, HW1F simplifies to Vasicek with b = theta/a
    a = 0.1
    sigma = 0.01
    theta_val = 0.005  # corresponds to b = 0.05
    model = HullWhite1FModel(a=a, sigma=sigma, theta=lambda t: theta_val)
    assert model.zcb_price(0.05, 0.0, 0.0) == 1.0

    price = model.zcb_price(0.05, 0.0, 1.0)
    vasicek_model = VasicekModel(a=a, b=theta_val / a, sigma=sigma)
    expected_price = vasicek_model.zcb_price(0.05, 1.0)

    assert price == pytest.approx(expected_price, rel=1e-3)


def test_hull_white_1f_monte_carlo_convergence():
    model = HullWhite1FModel(a=0.1, sigma=0.02, theta=lambda t: 0.01 + 0.005 * t)
    r0 = 0.04
    T = 2.0

    exact_price = model.zcb_price(r0, 0.0, T)
    mc = MonteCarloEngine(model, n_paths=20000, n_steps=100, seed=42)
    mc_price = mc.price_zcb(r0, T)
    assert exact_price == pytest.approx(mc_price, rel=0.02)


def test_hull_white_2f_zcb_pricing():
    model = HullWhite2FModel(
        a=0.1, b=0.05, sigma1=0.01, sigma2=0.02, rho=0.5, phi=lambda t: 0.03
    )
    assert model.zcb_price(0.01, 0.01, 0.0, 0.0) == 1.0
    price = model.zcb_price(0.01, 0.01, 0.0, 1.0)
    assert 0.0 < price < 1.0


def test_hull_white_2f_monte_carlo_convergence():
    model = HullWhite2FModel(
        a=0.1, b=0.2, sigma1=0.02, sigma2=0.01, rho=-0.3, phi=lambda t: 0.02
    )
    x0, y0 = 0.01, -0.005
    T = 1.0

    exact_price = model.zcb_price(x0, y0, 0.0, T)
    mc = MonteCarloEngine(model, n_paths=20000, n_steps=100, seed=42)
    mc_price = mc.price_zcb((x0, y0), T)
    assert exact_price == pytest.approx(mc_price, rel=0.02)


def test_shifted_cir_zcb_pricing():
    model = ShiftedCIRModel(a=0.1, b=0.05, sigma=0.01, shift=-0.02)
    assert model.zcb_price(0.05, 0.0) == 1.0
    price = model.zcb_price(0.05, 1.0)

    cir_model = CIRModel(a=0.1, b=0.05, sigma=0.01)
    # The Shifted CIR price should match CIR price evaluated at (r_t - shift) * exp(-shift*tau)
    expected_price = cir_model.zcb_price(0.05 - (-0.02), 1.0) * np.exp(-(-0.02) * 1.0)
    assert price == pytest.approx(expected_price, rel=1e-5)


def test_shifted_cir_monte_carlo_convergence():
    model = ShiftedCIRModel(a=0.2, b=0.05, sigma=0.05, shift=-0.01)
    r0 = 0.02  # equivalent to x0 = 0.03
    T = 2.0

    exact_price = model.zcb_price(r0, T)
    mc = MonteCarloEngine(model, n_paths=20000, n_steps=100, seed=42)
    mc_price = mc.price_zcb(r0, T)
    assert exact_price == pytest.approx(mc_price, rel=0.02)


def test_shifted_lognormal_monte_carlo():
    model = ShiftedLognormalModel(a=0.2, theta=0.01, sigma=0.1, shift=-0.02)
    r0 = 0.05
    T = 1.0

    # Just verify the monte carlo runs without error, as analytical solution is not implemented.
    mc = MonteCarloEngine(model, n_paths=1000, n_steps=50, seed=42)
    mc_price = mc.price_zcb(r0, T)
    assert 0.0 < mc_price < 1.0


def test_calibration_vasicek():
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
        r[t] = max(r[t], 1e-8)

    a_est, b_est, sigma_est = calibrate_cir(r, dt)
    assert sigma_est == pytest.approx(sigma, rel=0.1)
