"""Unit tests for Value at Risk (VaR) and Expected Shortfall (ES)."""

import numpy as np
import pytest

from src.portfolio.var import (
    historical_expected_shortfall,
    historical_var,
    parametric_expected_shortfall,
    parametric_var,
)


def test_historical_var():
    """Test Historical VaR calculation."""
    # A distribution of P&L from -100 to +100
    pnl = np.linspace(-100, 100, 1001)  # 1001 points
    # 99% VaR: the 1st percentile.
    # 1% of 1000 is 10. The 10th index from the bottom is around -98.
    var_99 = historical_var(pnl, confidence_level=0.99)
    assert np.isclose(var_99, 98.0)

    # 95% VaR: the 5th percentile.
    var_95 = historical_var(pnl, confidence_level=0.95)
    assert np.isclose(var_95, 90.0)


def test_historical_expected_shortfall():
    """Test Historical Expected Shortfall calculation."""
    pnl = np.linspace(-100, 100, 1001)

    # 99% VaR is -98. The tail is [-100, -99.8, ..., -98].
    # Expected shortfall should be the average of these tail losses.
    var_99 = historical_var(pnl, 0.99)
    es_99 = historical_expected_shortfall(pnl, 0.99)

    assert es_99 > var_99
    assert np.isclose(es_99, 99.0)


def test_historical_var_invalid_confidence():
    """Test invalid confidence levels for historical VaR."""
    pnl = np.array([-10, 0, 10])
    with pytest.raises(ValueError):
        historical_var(pnl, confidence_level=1.5)
    with pytest.raises(ValueError):
        historical_expected_shortfall(pnl, confidence_level=-0.5)


def test_parametric_var():
    """Test Parametric VaR calculation."""
    portfolio_value = 1_000_000
    duration = 5.0
    yield_volatility = 0.01  # 100 bps

    # At 99% confidence, z-score is ~2.326
    var_99 = parametric_var(portfolio_value, duration, yield_volatility, 0.99)
    # expected: 1,000,000 * 5.0 * 0.01 * 2.32634787 = 116,317.39
    assert np.isclose(var_99, 116317.39, rtol=1e-4)

    # At 95% confidence, z-score is ~1.645
    var_95 = parametric_var(portfolio_value, duration, yield_volatility, 0.95)
    assert np.isclose(var_95, 82242.68, rtol=1e-4)


def test_parametric_expected_shortfall():
    """Test Parametric Expected Shortfall calculation."""
    portfolio_value = 1_000_000
    duration = 5.0
    yield_volatility = 0.01

    var_99 = parametric_var(portfolio_value, duration, yield_volatility, 0.99)
    es_99 = parametric_expected_shortfall(
        portfolio_value, duration, yield_volatility, 0.99
    )

    assert es_99 > var_99
    # For a normal distribution, ES at 99% is approx 2.665 * std_dev
    # std_dev = 1,000,000 * 5.0 * 0.01 = 50,000
    # 50,000 * 2.6652 = 133,260
    assert np.isclose(es_99, 133260.72, rtol=1e-4)


def test_parametric_var_invalid_confidence():
    """Test invalid confidence levels for parametric VaR."""
    with pytest.raises(ValueError):
        parametric_var(100, 5, 0.01, 1.0)
    with pytest.raises(ValueError):
        parametric_expected_shortfall(100, 5, 0.01, 0.0)
