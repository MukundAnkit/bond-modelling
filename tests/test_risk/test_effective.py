"""Tests for Effective Duration and Convexity."""

import pytest

from src.instruments.bond import Bond


@pytest.fixture
def par_bond() -> Bond:
    return Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)


@pytest.fixture
def zcb_annual() -> Bond:
    return Bond(face_value=100, coupon_rate=0.0, maturity=5.0, freq=1)


# ---------------------------------------------------------------------------
# Effective Duration
# ---------------------------------------------------------------------------


def test_effective_duration_matches_modified(par_bond: Bond) -> None:
    from src.risk.duration import modified_duration
    from src.risk.effective import effective_duration

    y = 0.05
    effd = effective_duration(par_bond, y)
    modd = modified_duration(par_bond, y)
    assert effd == pytest.approx(modd, abs=2e-5)


def test_effective_duration_zcb_matches_modified(zcb_annual: Bond) -> None:
    from src.risk.duration import modified_duration
    from src.risk.effective import effective_duration

    y = 0.03
    effd = effective_duration(zcb_annual, y)
    modd = modified_duration(zcb_annual, y)
    assert effd == pytest.approx(modd, abs=1e-4)


def test_effective_duration_negative_yield(par_bond: Bond) -> None:
    from src.risk.effective import effective_duration

    effd = effective_duration(par_bond, -0.005)
    assert effd > 0.0


def test_effective_duration_zero_yield(par_bond: Bond) -> None:
    from src.risk.effective import effective_duration

    effd = effective_duration(par_bond, 0.0)
    assert effd > 0.0


# ---------------------------------------------------------------------------
# Effective Convexity
# ---------------------------------------------------------------------------


def test_effective_convexity_matches_analytical(par_bond: Bond) -> None:
    from src.risk.convexity import convexity
    from src.risk.effective import effective_convexity

    y = 0.05
    effcx = effective_convexity(par_bond, y)
    cx = convexity(par_bond, y)
    assert effcx == pytest.approx(cx, abs=1e-3)


def test_effective_convexity_zcb_closed_form(zcb_annual: Bond) -> None:
    from src.risk.effective import effective_convexity

    y = 0.03
    t = zcb_annual.maturity
    expected = t * (t + 1.0) / (1.0 + y) ** 2
    effcx = effective_convexity(zcb_annual, y)
    assert effcx == pytest.approx(expected, abs=5e-3)


def test_effective_convexity_always_positive(par_bond: Bond) -> None:
    from src.risk.effective import effective_convexity

    for y in [0.0, 0.02, 0.05, 0.10]:
        assert effective_convexity(par_bond, y) > 0.0


def test_effective_convexity_small_bump_reduces_error(par_bond: Bond) -> None:
    from src.risk.convexity import convexity
    from src.risk.effective import effective_convexity

    y = 0.05
    cx_target = convexity(par_bond, y)
    # Central-difference truncation error is O(bump^2) — a bump of 1e-2
    # should have ~100x the error of a bump of 1e-3.
    err_large = abs(effective_convexity(par_bond, y, bump=1e-2) - cx_target)
    err_small = abs(effective_convexity(par_bond, y, bump=1e-3) - cx_target)
    assert err_small < err_large
