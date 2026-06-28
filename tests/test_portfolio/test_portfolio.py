"""Tests for the portfolio risk and aggregation engine."""

import numpy as np
import pytest

from src.curve.nelson_siegel import NelsonSiegelCurve
from src.instruments.bond import Bond
from src.portfolio.portfolio import Portfolio
from src.portfolio.position import Position


@pytest.fixture
def base_curve() -> NelsonSiegelCurve:
    """Fixture providing a standard Nelson-Siegel curve."""
    # level=5%, slope=-2% (upward sloping), curvature=2%, decay=2.0 years
    return NelsonSiegelCurve(beta0=0.05, beta1=-0.02, beta2=0.02, tau=2.0)


@pytest.fixture
def bond_portfolio() -> Portfolio:
    """Fixture providing a sample bond portfolio with two positions."""
    # Position 1: 5-year, 4% coupon bond, 1000 units (face value 1,000,000)
    bond1 = Bond(face_value=1000.0, coupon_rate=0.04, maturity=5.0, freq=2)
    pos1 = Position(bond=bond1, quantity=1000)

    # Position 2: 10-year, 5% coupon bond, 500 units (face value 500,000)
    bond2 = Bond(face_value=1000.0, coupon_rate=0.05, maturity=10.0, freq=2)
    pos2 = Position(bond=bond2, quantity=500)

    port = Portfolio()
    port.add_position(pos1)
    port.add_position(pos2)
    return port


def test_position_market_value(base_curve: NelsonSiegelCurve) -> None:
    """Test market value and individual risk metrics on a single position."""
    bond = Bond(face_value=100.0, coupon_rate=0.05, maturity=2.0, freq=2)
    pos = Position(bond=bond, quantity=1000)

    # Price should equal present value of cash flows using the curve
    mv = pos.market_value(base_curve)
    # The yield for 2.0y is base_curve.yield_rate(2.0)
    expected_yield = base_curve.yield_rate(2.0)
    # Cash flows: 2.5 at 0.5, 1.0, 1.5, and 102.5 at 2.0
    # Yield is semi-annually compounded
    rate_per_period = expected_yield / 2.0
    expected_price = (
        2.5 / (1 + rate_per_period) ** 1
        + 2.5 / (1 + rate_per_period) ** 2
        + 2.5 / (1 + rate_per_period) ** 3
        + 102.5 / (1 + rate_per_period) ** 4
    )
    assert mv == pytest.approx(expected_price * 1000, abs=1e-8)


def test_portfolio_aggregation(
    bond_portfolio: Portfolio, base_curve: NelsonSiegelCurve
) -> None:
    """Test aggregate market value, weights, duration, convexity, and DV01."""
    port = bond_portfolio
    mv1 = port.positions[0].market_value(base_curve)
    mv2 = port.positions[1].market_value(base_curve)
    total_mv = mv1 + mv2

    assert port.market_value(base_curve) == pytest.approx(total_mv, abs=1e-8)

    # Weights
    weights = port.weights(base_curve)
    assert weights[0] == pytest.approx(mv1 / total_mv, abs=1e-8)
    assert weights[1] == pytest.approx(mv2 / total_mv, abs=1e-8)

    # Duration & Convexity
    d1 = port.positions[0].duration(base_curve)
    d2 = port.positions[1].duration(base_curve)
    expected_duration = weights[0] * d1 + weights[1] * d2
    assert port.duration(base_curve) == pytest.approx(expected_duration, abs=1e-8)

    cx1 = port.positions[0].convexity(base_curve)
    cx2 = port.positions[1].convexity(base_curve)
    expected_convexity = weights[0] * cx1 + weights[1] * cx2
    assert port.convexity(base_curve) == pytest.approx(expected_convexity, abs=1e-8)

    # DV01
    dv01_1 = port.positions[0].dv01(base_curve)
    dv01_2 = port.positions[1].dv01(base_curve)
    assert port.dv01(base_curve) == pytest.approx(dv01_1 + dv01_2, abs=1e-8)


def test_portfolio_key_rate_duration(
    bond_portfolio: Portfolio, base_curve: NelsonSiegelCurve
) -> None:
    """Test portfolio KRD aggregation and sum relationship to overall duration."""
    port = bond_portfolio
    tenors = np.array([1.0, 3.0, 5.0, 7.0, 10.0, 30.0])
    krds = port.key_rate_duration(base_curve, tenors)

    assert len(krds) == len(tenors)
    # The sum of all Key Rate Durations should equal the overall portfolio duration
    assert np.sum(krds) == pytest.approx(port.duration(base_curve), abs=0.1)


def test_portfolio_stress_pnl(
    bond_portfolio: Portfolio, base_curve: NelsonSiegelCurve
) -> None:
    """Test portfolio PnL estimation under stress scenarios."""
    port = bond_portfolio
    # Run steepener stress scenario
    pnl = port.stress_pnl(base_curve, "steepener")
    # P&L should be a float
    assert isinstance(pnl, float)
