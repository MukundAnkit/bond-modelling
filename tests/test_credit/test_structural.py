"""Unit tests for Structural Credit Models (Merton)."""

import pytest

from src.credit.structural import MertonModel, MertonJumpDiffusionModel


def test_merton_model_equity():
    # Asset value V = 100, Debt face D = 80, T = 1, r = 0.05, sigma = 0.20
    model = MertonModel(V=100.0, D=80.0, T=1.0, r=0.05, sigma_V=0.20)

    # Expected Equity Value is essentially a Call Option on V with strike D
    equity = model.equity_value()

    # Expected Debt Value is V - equity
    debt_val = model.debt_value()

    assert equity > 0
    assert debt_val > 0
    assert equity + debt_val == pytest.approx(100.0)


def test_distance_to_default():
    model = MertonModel(V=100.0, D=80.0, T=1.0, r=0.05, sigma_V=0.20)
    dd = model.distance_to_default()

    # d2 in Black-Scholes
    # ln(100/80) + (0.05 - 0.20^2 / 2)*1.0 = 0.2231 + 0.03 = 0.2531
    # 0.2531 / 0.20 = 1.2657
    assert dd == pytest.approx(1.2657, rel=1e-3)


def test_default_probability():
    model = MertonModel(V=100.0, D=80.0, T=1.0, r=0.05, sigma_V=0.20)
    pd = model.probability_of_default()

    # PD = N(-dd)
    # N(-1.2657) ~ 0.1028
    assert pd == pytest.approx(0.1028, rel=1e-3)


def test_credit_spread():
    model = MertonModel(V=100.0, D=80.0, T=1.0, r=0.05, sigma_V=0.20)
    spread = model.credit_spread()

    # Spread = - (1/T) * ln(Debt / (D * exp(-rT)))
    # D * exp(-rT) = 80 * exp(-0.05) = 76.098
    # Debt Value = V - equity
    # Wait, we can just check if spread is positive and reasonable
    assert spread > 0
    assert spread < 0.10


def test_merton_jump_diffusion_equity():
    model = MertonJumpDiffusionModel(
        V=100.0,
        D=80.0,
        T=1.0,
        r=0.05,
        sigma_V=0.20,
        lambda_j=0.5,
        mu_j=-0.1,
        sigma_j=0.3,
    )

    equity = model.equity_value()
    debt_val = model.debt_value()

    assert equity > 0
    assert debt_val > 0
    assert equity + debt_val == pytest.approx(100.0)

    base_model = MertonModel(V=100.0, D=80.0, T=1.0, r=0.05, sigma_V=0.20)
    base_equity = base_model.equity_value()
    
    # Due to increased tail risk, equity (call option) is more valuable
    assert equity > base_equity

