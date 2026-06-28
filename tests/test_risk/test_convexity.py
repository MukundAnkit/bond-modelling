"""Tests for Convexity calculation."""

import pytest

from src.instruments.bond import Bond
from src.instruments.pricing import price


@pytest.fixture
def par_bond() -> Bond:
    return Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)


@pytest.fixture
def zcb_annual() -> Bond:
    return Bond(face_value=100, coupon_rate=0.0, maturity=5.0, freq=1)


@pytest.fixture
def zcb_semi() -> Bond:
    return Bond(face_value=100, coupon_rate=0.0, maturity=5.0, freq=2)


# ---------------------------------------------------------------------------
# Convexity
# ---------------------------------------------------------------------------


def test_convexity_zcb_annual_analytical(zcb_annual: Bond) -> None:
    from src.risk.convexity import convexity

    y = 0.03
    t = 5.0
    cx = convexity(zcb_annual, y)
    expected = t * (t + 1.0) / (1 + y) ** 2
    assert cx == pytest.approx(expected, abs=1e-10)


def test_convexity_zcb_semi_analytical(zcb_semi: Bond) -> None:
    from src.risk.convexity import convexity

    y = 0.03
    t = 5.0
    m = 2.0
    cx = convexity(zcb_semi, y)
    expected = t * (t + 1.0 / m) / (1 + y / m) ** 2
    assert cx == pytest.approx(expected, abs=1e-10)


def test_convexity_positive(par_bond: Bond) -> None:
    from src.risk.convexity import convexity

    for y in [0.01, 0.05, 0.10]:
        assert convexity(par_bond, y) > 0.0


def test_convexity_higher_coupon_lower() -> None:
    from src.risk.convexity import convexity

    low = Bond(100, 0.03, 5.0, 2)
    high = Bond(100, 0.08, 5.0, 2)
    y = 0.05
    assert convexity(high, y) < convexity(low, y)


def test_convexity_longer_maturity_higher() -> None:
    from src.risk.convexity import convexity

    short = Bond(100, 0.05, 2.0, 2)
    long_ = Bond(100, 0.05, 10.0, 2)
    y = 0.05
    assert convexity(short, y) < convexity(long_, y)


def test_convexity_numerical_cross_check(par_bond: Bond) -> None:
    from src.risk.convexity import convexity

    y = 0.05
    eps = 1e-4
    analytical = convexity(par_bond, y)
    p = price(par_bond, y)
    p_up = price(par_bond, y + eps)
    p_down = price(par_bond, y - eps)
    numerical = (p_up - 2 * p + p_down) / (eps * eps * p)
    assert analytical == pytest.approx(numerical, abs=1e-2)


def test_convexity_yield_zero() -> None:
    from src.risk.convexity import convexity

    b = Bond(100, 0.06, 3.0, 2)
    cx = convexity(b, 0.0)
    assert cx > 0.0


def test_convexity_single_period() -> None:
    from src.risk.convexity import convexity

    b = Bond(100, 0.05, 0.5, 2)
    y = 0.05
    cx = convexity(b, y)
    expected = 2.0 / (b.freq**2 * (1 + y / b.freq) ** 2)
    assert cx == pytest.approx(expected, abs=1e-10)


def test_convexity_negative_yield() -> None:
    from src.risk.convexity import convexity

    b = Bond(100, 0.02, 3.0, 1)
    cx = convexity(b, -0.01)
    assert cx > 0.0
