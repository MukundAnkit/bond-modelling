"""Tests for Key Rate Duration calculations."""

import pytest

from src.instruments.bond import Bond
from src.risk.duration import modified_duration


@pytest.fixture
def par_bond_5yr() -> Bond:
    return Bond(face_value=100, coupon_rate=0.05, maturity=5.0, freq=2)


@pytest.fixture
def zcb_annual() -> Bond:
    return Bond(face_value=100, coupon_rate=0.0, maturity=5.0, freq=1)


# ---------------------------------------------------------------------------
# Key Rate Durations
# ---------------------------------------------------------------------------


def test_krd_sum_equals_modified_duration(par_bond_5yr: Bond) -> None:
    from src.risk.key_rate_duration import key_rate_durations

    y = 0.05
    krd = key_rate_durations(par_bond_5yr, y)
    krd_sum = sum(krd.values())
    modd = modified_duration(par_bond_5yr, y)
    assert krd_sum == pytest.approx(modd, rel=1e-3)


def test_krd_all_non_negative(par_bond_5yr: Bond) -> None:
    from src.risk.key_rate_duration import key_rate_durations

    y = 0.05
    krd = key_rate_durations(par_bond_5yr, y)
    for tenor, value in krd.items():
        assert value >= -1e-10, f"KRD at {tenor}yr is negative: {value}"


def test_krd_zcb_concentrated_at_maturity(zcb_annual: Bond) -> None:
    from src.risk.key_rate_duration import key_rate_durations

    y = 0.03
    krd = key_rate_durations(zcb_annual, y)
    maturity_krd = krd[zcb_annual.maturity]
    total = sum(krd.values())
    # For a ZCB, essentially all KRD should be at maturity
    assert maturity_krd / total > 0.95


def test_krd_custom_key_rates(par_bond_5yr: Bond) -> None:
    from src.risk.key_rate_duration import key_rate_durations

    y = 0.05
    custom = [1.0, 3.0, 5.0]
    krd = key_rate_durations(par_bond_5yr, y, key_rates=custom)
    assert set(krd.keys()) == set(custom)
    krd_sum = sum(krd.values())
    modd = modified_duration(par_bond_5yr, y)
    assert krd_sum == pytest.approx(modd, rel=1e-3)


def test_krd_single_period_bond() -> None:
    from src.risk.key_rate_duration import key_rate_durations

    b = Bond(100, 0.05, 0.5, 2)
    y = 0.05
    krd = key_rate_durations(b, y)
    # Single-period bond: all duration at 0.5yr
    total = sum(krd.values())
    modd = modified_duration(b, y)
    assert total == pytest.approx(modd, rel=1e-2)
