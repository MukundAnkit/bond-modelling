"""Unit tests for Value at Risk (VaR) and Expected Shortfall (ES)."""

import numpy as np
import pytest

from src.curve.nelson_siegel import NelsonSiegelCurve
from src.instruments.bond import Bond
from src.portfolio.portfolio import Portfolio
from src.portfolio.position import Position
from src.portfolio.var import (
    cornish_fisher_expected_shortfall,
    cornish_fisher_var,
    full_revaluation_pnl,
    full_revaluation_var,
    historical_expected_shortfall,
    historical_var,
    pot_expected_shortfall,
)


def test_historical_var():
    """Test Historical VaR calculation."""
    pnl = np.linspace(-100, 100, 1001)
    var_99 = historical_var(pnl, confidence_level=0.99)
    assert np.isclose(var_99, 98.0)
    var_95 = historical_var(pnl, confidence_level=0.95)
    assert np.isclose(var_95, 90.0)


def test_historical_expected_shortfall():
    """Test Historical Expected Shortfall calculation."""
    pnl = np.linspace(-100, 100, 1001)
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


def test_full_revaluation_var():
    """Test Grid-based Full Revaluation VaR."""
    portfolio = Portfolio()
    bond = Bond(face_value=100, coupon_rate=0.05, maturity=5.0, freq=2)
    position = Position(bond=bond, quantity=1000)
    portfolio.add_position(position)

    base_curve = NelsonSiegelCurve(beta0=0.05, beta1=-0.02, beta2=0.02, tau=1.5)
    yield_shifts = np.linspace(-0.02, 0.02, 101)  # 101 shifts from -200bps to +200bps

    pnl = full_revaluation_pnl(portfolio, base_curve, yield_shifts)
    assert len(pnl) == 101

    # Check that positive yield shift (increase in rates) leads to negative P&L
    assert pnl[-1] < 0  # +200 bps
    assert pnl[0] > 0  # -200 bps

    var_99 = full_revaluation_var(portfolio, base_curve, yield_shifts, 0.99)
    assert var_99 > 0


def test_cornish_fisher_var_and_es():
    """Test Cornish-Fisher VaR and ES."""
    np.random.seed(42)
    pnl = np.random.normal(loc=0.0, scale=100.0, size=10000)

    cf_var = cornish_fisher_var(pnl, 0.99)
    cf_es = cornish_fisher_expected_shortfall(pnl, 0.99)

    assert cf_var > 0
    assert cf_es > cf_var


def test_pot_expected_shortfall():
    """Test POT Expected Shortfall calculation."""
    np.random.seed(42)
    # Generate student-t distributed fat tails
    pnl = np.random.standard_t(df=4, size=10000) * 100.0

    pot_es = pot_expected_shortfall(pnl, 0.99)
    hist_es = historical_expected_shortfall(pnl, 0.99)

    # They should both be valid positive ES values
    assert pot_es > 0
    assert hist_es > 0


def test_invalid_confidence_evt():
    pnl = np.random.normal(0, 1, 100)
    with pytest.raises(ValueError):
        cornish_fisher_var(pnl, 1.5)
    with pytest.raises(ValueError):
        cornish_fisher_expected_shortfall(pnl, 1.5)
    with pytest.raises(ValueError):
        pot_expected_shortfall(pnl, -0.5)
