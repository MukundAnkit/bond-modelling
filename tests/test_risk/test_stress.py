"""Tests for Basel IRBB stress scenarios."""

import pytest

from src.instruments.bond import Bond
from src.instruments.pricing import price


@pytest.fixture
def par_bond_5yr() -> Bond:
    return Bond(face_value=100, coupon_rate=0.05, maturity=5.0, freq=2)


@pytest.fixture
def long_bond() -> Bond:
    return Bond(face_value=100, coupon_rate=0.05, maturity=10.0, freq=2)


# ---------------------------------------------------------------------------
# Scenario keys
# ---------------------------------------------------------------------------


def test_irbb_returns_all_six_scenarios(par_bond_5yr: Bond) -> None:
    from src.risk.stress import irbb_stress_scenarios

    results = irbb_stress_scenarios(par_bond_5yr, 0.05)
    expected_keys = {
        "parallel_up",
        "parallel_down",
        "steepener",
        "flattener",
        "short_rate_up",
        "short_rate_down",
    }
    assert set(results.keys()) == expected_keys


def test_irbb_each_result_has_price_and_pnl(par_bond_5yr: Bond) -> None:
    from src.risk.stress import irbb_stress_scenarios

    results = irbb_stress_scenarios(par_bond_5yr, 0.05)
    for name, entry in results.items():
        assert "price" in entry, f"{name} missing 'price'"
        assert "pnl" in entry, f"{name} missing 'pnl'"


# ---------------------------------------------------------------------------
# Parallel scenarios
# ---------------------------------------------------------------------------


def test_parallel_up_lowers_price(par_bond_5yr: Bond) -> None:
    from src.risk.stress import irbb_stress_scenarios

    p0 = price(par_bond_5yr, 0.05)
    results = irbb_stress_scenarios(par_bond_5yr, 0.05)
    assert results["parallel_up"]["price"] < p0
    assert results["parallel_up"]["pnl"] < 0.0


def test_parallel_down_raises_price(par_bond_5yr: Bond) -> None:
    from src.risk.stress import irbb_stress_scenarios

    p0 = price(par_bond_5yr, 0.05)
    results = irbb_stress_scenarios(par_bond_5yr, 0.05)
    assert results["parallel_down"]["price"] > p0
    assert results["parallel_down"]["pnl"] > 0.0


def test_parallel_up_matches_exact_repricing(par_bond_5yr: Bond) -> None:
    from src.risk.stress import irbb_stress_scenarios

    y = 0.05
    results = irbb_stress_scenarios(par_bond_5yr, y)
    p_exact = price(par_bond_5yr, y + 0.01)
    assert results["parallel_up"]["price"] == pytest.approx(p_exact, abs=1e-10)


# ---------------------------------------------------------------------------
# Non-parallel scenarios: basic sanity
# ---------------------------------------------------------------------------


def test_steepener_hurts_long_bond_more(long_bond: Bond, par_bond_5yr: Bond) -> None:
    from src.risk.stress import irbb_stress_scenarios

    y = 0.05
    short_result = irbb_stress_scenarios(par_bond_5yr, y)
    long_result = irbb_stress_scenarios(long_bond, y)
    # Steepener raises long rates → long bond should lose more (in % terms)
    short_pnl_pct = short_result["steepener"]["pnl"] / price(par_bond_5yr, y)
    long_pnl_pct = long_result["steepener"]["pnl"] / price(long_bond, y)
    assert long_pnl_pct < short_pnl_pct


def test_flattener_short_bond_loses_long_bond_gains() -> None:
    """Flattener: short bonds lose, long bonds gain.

    Flattener raises short-term rates (bad for short bonds) and lowers
    long-term rates (good for very long bonds).
    """
    from src.risk.stress import irbb_stress_scenarios

    b_short = Bond(100, 0.03, 2.0, 2)
    b_long = Bond(100, 0.05, 30.0, 2)
    y = 0.04
    short_res = irbb_stress_scenarios(b_short, y)
    long_res = irbb_stress_scenarios(b_long, y)
    assert short_res["flattener"]["pnl"] < 0.0
    assert long_res["flattener"]["pnl"] > 0.0


def test_short_rate_up_lowers_price(par_bond_5yr: Bond) -> None:
    from src.risk.stress import irbb_stress_scenarios

    p0 = price(par_bond_5yr, 0.05)
    results = irbb_stress_scenarios(par_bond_5yr, 0.05)
    assert results["short_rate_up"]["price"] < p0
    assert results["short_rate_down"]["price"] > p0


# ---------------------------------------------------------------------------
# Consistency: parallel shock magnitude larger than short-rate shock for
# short-maturity bonds
# ---------------------------------------------------------------------------


def test_short_rate_symmetric_for_par_bond(par_bond_5yr: Bond) -> None:
    """Short-rate up/down P&L should be roughly symmetric.

    For a plain vanilla bond, a short-rate increase and a short-rate
    decrease of equal magnitude produce roughly opposite P&L
    (small asymmetry due to convexity).
    """
    from src.risk.stress import irbb_stress_scenarios

    y = 0.05
    results = irbb_stress_scenarios(par_bond_5yr, y)
    pnl_up = results["short_rate_up"]["pnl"]
    pnl_down = results["short_rate_down"]["pnl"]
    # Up = down in magnitude within 15% (convexity causes asymmetry,
    # and the 300bp short-rate shock amplifies the convexity effect)
    assert pnl_up == pytest.approx(-pnl_down, rel=0.15)
