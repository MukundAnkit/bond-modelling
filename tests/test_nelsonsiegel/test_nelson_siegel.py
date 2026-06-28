"""Tests for the Nelson-Siegel continuous curve optimization module."""

import numpy as np
import pytest

from src.curve.nelson_siegel import NelsonSiegelCurve


def test_nelson_siegel_evaluation_scalar() -> None:
    """Test evaluation of Nelson-Siegel curve for scalar maturities."""
    # y(t) = beta0 + beta1 * ((1 - e^{-t/tau}) / (t/tau))
    #        + beta2 * ((1 - e^{-t/tau}) / (t/tau) - e^{-t/tau})
    # Let beta0 = 0.06, beta1 = -0.02, beta2 = 0.04, tau = 1.5
    curve = NelsonSiegelCurve(beta0=0.06, beta1=-0.02, beta2=0.04, tau=1.5)

    # Test at t = 0 (limit is beta0 + beta1)
    assert curve.yield_rate(0.0) == pytest.approx(0.04, abs=1e-12)
    assert curve(0.0) == pytest.approx(0.04, abs=1e-12)

    # Test at t = 1.5 (t = tau)
    # factor = (1 - e^-1) / 1 = 1 - e^-1
    # multiplier1 = 1 - e^-1
    # multiplier2 = 1 - e^-1 - e^-1 = 1 - 2*e^-1
    e_inv = np.exp(-1.0)
    expected_y = 0.06 - 0.02 * (1.0 - e_inv) + 0.04 * (1.0 - 2.0 * e_inv)
    assert curve.yield_rate(1.5) == pytest.approx(expected_y, abs=1e-12)
    assert curve(1.5) == pytest.approx(expected_y, abs=1e-12)


def test_nelson_siegel_evaluation_vector() -> None:
    """Test vectorized evaluation of Nelson-Siegel curve."""
    curve = NelsonSiegelCurve(beta0=0.06, beta1=-0.02, beta2=0.04, tau=1.5)
    ts = np.array([0.0, 1.0, 2.0, 5.0])
    yields = curve.yield_rate(ts)

    assert isinstance(yields, np.ndarray)
    assert len(yields) == 4
    assert yields[0] == pytest.approx(0.04, abs=1e-12)

    # Verify matching scalar calculations
    for t, y in zip(ts, yields, strict=True):
        assert curve.yield_rate(t) == pytest.approx(y, abs=1e-12)


def test_nelson_siegel_properties() -> None:
    """Test property accessors and aliases."""
    curve = NelsonSiegelCurve(beta0=0.06, beta1=-0.02, beta2=0.04, tau=1.5)
    assert curve.beta0 == 0.06
    assert curve.beta1 == -0.02
    assert curve.beta2 == 0.04
    assert curve.tau == 1.5

    assert curve.level == 0.06
    assert curve.slope == -0.02
    assert curve.curvature == 0.04
    assert curve.decay == 1.5


def test_nelson_siegel_sse() -> None:
    """Test SSE computation."""
    curve = NelsonSiegelCurve(beta0=0.05, beta1=0.0, beta2=0.0, tau=1.0)
    maturities = np.array([1.0, 2.0, 3.0])
    spot_rates = np.array([0.05, 0.06, 0.07])
    # For a flat 5% curve, yield_rate is always 0.05.
    # Errors are: 0.0, 0.01, 0.02
    # SSE = 0^2 + 0.01^2 + 0.02^2 = 0.0001 + 0.0004 = 0.0005
    assert curve.sse(maturities, spot_rates) == pytest.approx(0.0005, abs=1e-12)


def test_nelson_siegel_fit_flat() -> None:
    """Test fitting the curve on flat yield curve data."""
    maturities = np.array([1.0, 2.0, 3.0, 5.0, 7.0, 10.0])
    spot_rates = np.full_like(maturities, 0.05)

    curve = NelsonSiegelCurve.fit(maturities, spot_rates)
    assert curve.level == pytest.approx(0.05, abs=1e-4)
    assert curve.slope == pytest.approx(0.0, abs=1e-4)
    assert curve.curvature == pytest.approx(0.0, abs=1e-4)


def test_nelson_siegel_fit_known() -> None:
    """Test recovering known parameters from synthesized curve data."""
    true_beta0 = 0.06
    true_beta1 = -0.02
    true_beta2 = 0.04
    true_tau = 1.5
    true_curve = NelsonSiegelCurve(true_beta0, true_beta1, true_beta2, true_tau)

    maturities = np.array([0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0])
    spot_rates = true_curve.yield_rate(maturities)

    fitted_curve = NelsonSiegelCurve.fit(maturities, spot_rates)
    assert fitted_curve.level == pytest.approx(true_beta0, abs=1e-4)
    assert fitted_curve.slope == pytest.approx(true_beta1, abs=1e-4)
    assert fitted_curve.curvature == pytest.approx(true_beta2, abs=1e-4)
    assert fitted_curve.decay == pytest.approx(true_tau, abs=1e-4)


def test_nelson_siegel_fit_bounds() -> None:
    """Test that fitting respects parameters bounds (beta0 > 0, tau > 0)."""
    # Create extreme data where unconstrained optimization might yield negative values
    maturities = np.array([0.5, 1.0, 2.0])
    spot_rates = np.array([-0.05, -0.04, -0.03])  # negative rates

    fitted_curve = NelsonSiegelCurve.fit(maturities, spot_rates)
    # beta0 and tau should be strictly positive (>= their lower bounds)
    assert fitted_curve.level >= 1e-6
    assert fitted_curve.decay >= 1e-6


def test_nelson_siegel_fit_validation() -> None:
    """Test validation errors for curve fitting."""
    maturities = np.array([1.0, 2.0])
    spot_rates = np.array([0.05])
    with pytest.raises(ValueError, match="same length"):
        NelsonSiegelCurve.fit(maturities, spot_rates)

    maturities = np.array([])
    spot_rates = np.array([])
    with pytest.raises(ValueError, match="empty"):
        NelsonSiegelCurve.fit(maturities, spot_rates)

    maturities = np.array([-1.0, 2.0])
    spot_rates = np.array([0.04, 0.05])
    with pytest.raises(ValueError, match="positive"):
        NelsonSiegelCurve.fit(maturities, spot_rates)
