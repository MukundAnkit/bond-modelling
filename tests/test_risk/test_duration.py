"""Tests for Macaulay and Modified Duration calculations."""

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
# Macaulay Duration
# ---------------------------------------------------------------------------


def test_macaulay_par_bond_less_than_maturity(par_bond: Bond) -> None:
    from src.risk.duration import macaulay_duration

    macd = macaulay_duration(par_bond, 0.05)
    assert macd < 3.0
    assert macd > 0.0


def test_macaulay_zcb_annual_equals_maturity(zcb_annual: Bond) -> None:
    from src.risk.duration import macaulay_duration

    macd = macaulay_duration(zcb_annual, 0.03)
    assert macd == pytest.approx(5.0, abs=1e-10)


def test_macaulay_zcb_semi_equals_maturity(zcb_semi: Bond) -> None:
    from src.risk.duration import macaulay_duration

    macd = macaulay_duration(zcb_semi, 0.03)
    assert macd == pytest.approx(5.0, abs=1e-10)


def test_macaulay_higher_coupon_lower_duration() -> None:
    from src.risk.duration import macaulay_duration

    low_coupon = Bond(100, 0.03, 5.0, 2)
    high_coupon = Bond(100, 0.08, 5.0, 2)
    d_low = macaulay_duration(low_coupon, 0.05)
    d_high = macaulay_duration(high_coupon, 0.05)
    assert d_high < d_low


def test_macaulay_longer_maturity_higher_duration() -> None:
    from src.risk.duration import macaulay_duration

    short = Bond(100, 0.05, 2.0, 2)
    long_ = Bond(100, 0.05, 10.0, 2)
    assert macaulay_duration(short, 0.05) < macaulay_duration(long_, 0.05)


def test_macaulay_yield_zero() -> None:
    from src.risk.duration import macaulay_duration

    b = Bond(100, 0.06, 3.0, 2)
    macd = macaulay_duration(b, 0.0)
    n = b.periods
    p = 100 + n * b.coupon_payment
    time_sum = sum((t / b.freq) * b.coupon_payment for t in range(1, n))
    time_sum += (n / b.freq) * (b.coupon_payment + b.face_value)
    expected = time_sum / p
    assert macd == pytest.approx(expected, abs=1e-10)


def test_macaulay_negative_yield() -> None:
    from src.risk.duration import macaulay_duration

    b = Bond(100, 0.02, 3.0, 1)
    macd = macaulay_duration(b, -0.01)
    assert macd > 0.0
    assert macd < 3.0


def test_macaulay_single_period() -> None:
    from src.risk.duration import macaulay_duration

    b = Bond(100, 0.05, 0.5, 2)
    macd = macaulay_duration(b, 0.05)
    assert macd == pytest.approx(0.5, abs=1e-10)


# ---------------------------------------------------------------------------
# Modified Duration
# ---------------------------------------------------------------------------


def test_modified_from_macaulay(par_bond: Bond) -> None:
    from src.risk.duration import macaulay_duration, modified_duration

    y = 0.05
    macd = macaulay_duration(par_bond, y)
    modd = modified_duration(par_bond, y)
    assert modd == pytest.approx(macd / (1 + y / par_bond.freq), abs=1e-12)


def test_modified_zcb_annual(zcb_annual: Bond) -> None:
    from src.risk.duration import modified_duration

    y = 0.03
    modd = modified_duration(zcb_annual, y)
    expected = 5.0 / (1 + y)
    assert modd == pytest.approx(expected, abs=1e-10)


def test_modified_par_bond(par_bond: Bond) -> None:
    from src.risk.duration import macaulay_duration, modified_duration

    y = 0.05
    macd = macaulay_duration(par_bond, y)
    modd = modified_duration(par_bond, y)
    expected = macd / (1 + y / par_bond.freq)
    assert modd == pytest.approx(expected, abs=1e-12)


def test_modified_positive_for_all_bonds() -> None:
    from src.risk.duration import modified_duration

    for y in [0.01, 0.05, 0.10]:
        b = Bond(100, 0.05, 5.0, 2)
        assert modified_duration(b, y) > 0.0


def test_modified_numerical_cross_check() -> None:
    from src.risk.duration import modified_duration

    b = Bond(100, 0.05, 5.0, 2)
    y = 0.05
    eps = 1e-6
    analytical = modified_duration(b, y)
    p_up = price(b, y + eps)
    p_down = price(b, y - eps)
    numerical = -(p_up - p_down) / (2 * eps * price(b, y))
    assert analytical == pytest.approx(numerical, abs=1e-6)


def test_modified_yield_zero() -> None:
    from src.risk.duration import macaulay_duration, modified_duration

    b = Bond(100, 0.06, 3.0, 2)
    y = 0.0
    modd = modified_duration(b, y)
    macd = macaulay_duration(b, y)
    expected = macd / (1 + y / b.freq)
    assert modd == pytest.approx(expected, abs=1e-12)
