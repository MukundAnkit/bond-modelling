"""Tests for Dollar Duration, DV01, and Dollar Convexity."""

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
# Dollar Duration
# ---------------------------------------------------------------------------


def test_dollar_duration_equals_modd_times_price(par_bond: Bond) -> None:
    from src.risk.dollar_measures import dollar_duration
    from src.risk.duration import modified_duration

    y = 0.05
    dd = dollar_duration(par_bond, y)
    expected = modified_duration(par_bond, y) * price(par_bond, y)
    assert dd == pytest.approx(expected, abs=1e-12)


def test_dollar_duration_positive(par_bond: Bond) -> None:
    from src.risk.dollar_measures import dollar_duration

    for y in [0.01, 0.05, 0.10]:
        assert dollar_duration(par_bond, y) > 0.0


def test_dollar_duration_longer_maturity_higher() -> None:
    from src.risk.dollar_measures import dollar_duration

    short = Bond(100, 0.05, 2.0, 2)
    long_ = Bond(100, 0.05, 10.0, 2)
    y = 0.05
    assert dollar_duration(short, y) < dollar_duration(long_, y)


# ---------------------------------------------------------------------------
# DV01
# ---------------------------------------------------------------------------


def test_dv01_equals_dd_over_10000(par_bond: Bond) -> None:
    from src.risk.dollar_measures import dollar_duration, dv01

    y = 0.05
    assert dv01(par_bond, y) == pytest.approx(
        dollar_duration(par_bond, y) / 10_000, abs=1e-14
    )


def test_dv01_numerical_cross_check(par_bond: Bond) -> None:
    from src.risk.dollar_measures import dv01

    y = 0.05
    analytical = dv01(par_bond, y)
    # Numerical: reprice at +1bp
    p0 = price(par_bond, y)
    p1 = price(par_bond, y + 0.0001)
    numerical = abs(p1 - p0)
    assert analytical == pytest.approx(numerical, rel=1e-3)


def test_dv01_zcb_closed_form(zcb_annual: Bond) -> None:
    from src.risk.dollar_measures import dv01

    y = 0.03
    d = dv01(zcb_annual, y)
    # For ZCB: DV01 = T * P / (1+y) / 10000
    p = price(zcb_annual, y)
    expected = 5.0 / (1 + y) * p / 10_000
    assert d == pytest.approx(expected, abs=1e-10)


# ---------------------------------------------------------------------------
# Dollar Convexity
# ---------------------------------------------------------------------------


def test_dollar_convexity_equals_cx_times_price(par_bond: Bond) -> None:
    from src.risk.convexity import convexity
    from src.risk.dollar_measures import dollar_convexity

    y = 0.05
    dc = dollar_convexity(par_bond, y)
    expected = convexity(par_bond, y) * price(par_bond, y)
    assert dc == pytest.approx(expected, abs=1e-10)


def test_dollar_convexity_positive(par_bond: Bond) -> None:
    from src.risk.dollar_measures import dollar_convexity

    for y in [0.01, 0.05, 0.10]:
        assert dollar_convexity(par_bond, y) > 0.0
