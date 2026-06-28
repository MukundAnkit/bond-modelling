"""Tests for price shock simulation using Taylor expansion."""

import pytest

from src.instruments.bond import Bond
from src.instruments.pricing import price


@pytest.fixture
def par_bond() -> Bond:
    return Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)


@pytest.fixture
def zcb_annual() -> Bond:
    return Bond(face_value=100, coupon_rate=0.0, maturity=5.0, freq=1)


# ---------------------------------------------------------------------------
# price_shock — returns ΔP
# ---------------------------------------------------------------------------


def test_shock_positive_yield_negative_delta(par_bond: Bond) -> None:
    from src.risk.shock import price_shock

    dp = price_shock(par_bond, 0.05, 0.01)
    assert dp < 0.0


def test_shock_negative_yield_positive_delta(par_bond: Bond) -> None:
    from src.risk.shock import price_shock

    dp = price_shock(par_bond, 0.05, -0.01)
    assert dp > 0.0


def test_shock_zero_delta(par_bond: Bond) -> None:
    from src.risk.shock import price_shock

    dp = price_shock(par_bond, 0.05, 0.0)
    assert dp == pytest.approx(0.0, abs=1e-12)


def test_shock_one_bp_very_close_to_exact(par_bond: Bond) -> None:
    from src.risk.shock import price_shock, shocked_price

    y = 0.05
    delta = 0.0001
    p0 = price(par_bond, y)
    p_exact = price(par_bond, y + delta)
    p_taylor = shocked_price(par_bond, y, delta)
    diff_exact = p_exact - p0
    diff_taylor = price_shock(par_bond, y, delta)
    assert diff_taylor == pytest.approx(diff_exact, abs=1e-4)
    assert p_taylor == pytest.approx(p_exact, abs=1e-4)


def test_shock_100bp_approximation_reasonable(par_bond: Bond) -> None:
    from src.risk.shock import shocked_price

    y = 0.05
    delta = 0.01
    p0 = price(par_bond, y)
    p_exact = price(par_bond, y + delta)
    p_taylor = shocked_price(par_bond, y, delta)
    error = abs(p_taylor - p_exact) / p0
    assert error < 0.005


def test_shock_asymmetric_positive_negative() -> None:
    from src.risk.shock import price_shock

    b = Bond(100, 0.05, 5.0, 2)
    y = 0.05
    dp_up = price_shock(b, y, 0.01)
    dp_down = price_shock(b, y, -0.01)
    assert abs(dp_up) < abs(dp_down)


def test_shock_includes_convexity_term() -> None:
    from src.risk.convexity import convexity
    from src.risk.duration import modified_duration
    from src.risk.shock import price_shock

    b = Bond(100, 0.05, 5.0, 2)
    y = 0.05
    delta = 0.01
    p = price(b, y)
    modd = modified_duration(b, y)
    cx = convexity(b, y)
    expected = -modd * p * delta + 0.5 * cx * p * delta**2
    assert price_shock(b, y, delta) == pytest.approx(expected, abs=1e-12)


# ---------------------------------------------------------------------------
# shocked_price — returns P + ΔP
# ---------------------------------------------------------------------------


def test_shocked_price_zero_delta_equals_price(par_bond: Bond) -> None:
    from src.risk.shock import shocked_price

    p = price(par_bond, 0.05)
    assert shocked_price(par_bond, 0.05, 0.0) == pytest.approx(p, abs=1e-12)


def test_shocked_price_positive_delta_lower(par_bond: Bond) -> None:
    from src.risk.shock import shocked_price

    p0 = price(par_bond, 0.05)
    p1 = shocked_price(par_bond, 0.05, 0.01)
    assert p1 < p0
