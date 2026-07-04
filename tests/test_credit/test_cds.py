"""Unit tests for Credit Default Swaps (CDS)."""

import datetime

import numpy as np
import pytest

from src.credit.cds import (
    CDS,
    cds_par_spread,
    cds_premium_leg,
    cds_protection_leg,
    isda_par_spread,
    isda_upfront_charge,
)


def test_cds_premium_leg():
    # Constant hazard rate and flat yield curve
    # lambda = 0.02, r = 0.04
    def curve(_):
        return 0.04

    def survival_curve(t):
        return np.exp(-0.02 * t)

    # 5-year CDS, spread = 100 bps
    cds = CDS(notional=10_000_000, spread=0.01, tenor=5.0, freq=4)

    pv_premium = cds_premium_leg(cds, curve, survival_curve)

    # Approximate analytic premium leg PV
    # PV = Spread * sum( e^(-r t_i) * S(t_i) * dt )
    # With dt = 0.25, and sum over 20 periods
    dt = 0.25
    expected_pv = 0.0
    for i in range(1, 21):
        t = i * dt
        expected_pv += 0.01 * dt * np.exp(-0.04 * t) * np.exp(-0.02 * t)

    expected_pv *= 10_000_000
    assert pv_premium == pytest.approx(expected_pv, rel=1e-3)


def test_cds_protection_leg():
    def curve(_):
        return 0.04

    def survival_curve(t):
        return np.exp(-0.02 * t)

    cds = CDS(notional=10_000_000, spread=0.01, tenor=5.0, freq=4)
    recovery_rate = 0.40

    pv_protection = cds_protection_leg(cds, curve, survival_curve, recovery_rate)

    # Approximate analytic protection leg PV
    # PV = (1 - R) * sum( e^(-r t_i) * (S(t_{i-1}) - S(t_i)) )
    dt = 0.25
    expected_pv = 0.0
    s_prev = 1.0
    for i in range(1, 21):
        t = i * dt
        s_curr = np.exp(-0.02 * t)
        # Assuming default occurs mid-period for discounting
        expected_pv += (
            (1 - recovery_rate) * np.exp(-0.04 * (t - dt / 2)) * (s_prev - s_curr)
        )
        s_prev = s_curr

    expected_pv *= 10_000_000
    assert pv_protection == pytest.approx(expected_pv, rel=1e-2)


def test_cds_par_spread():
    def curve(_):
        return 0.04

    def survival_curve(t):
        return np.exp(-0.02 * t)

    cds = CDS(notional=10_000_000, spread=0.0, tenor=5.0, freq=4)
    recovery_rate = 0.40

    par_spread = cds_par_spread(cds, curve, survival_curve, recovery_rate)

    # For a flat curve and constant hazard rate lambda:
    # Par Spread approx = lambda * (1 - R)
    # 0.02 * (1 - 0.4) = 0.012 = 120 bps
    assert par_spread == pytest.approx(0.012, rel=5e-2)


def test_isda_cds_model():
    valuation_date = datetime.date(2023, 9, 15)
    effective_date = datetime.date(2023, 9, 16)
    maturity_date = datetime.date(2028, 12, 20)

    def curve(t):
        return 0.03  # flat 3% curve

    recovery_rate = 0.40
    notional = 10_000_000

    # Standard coupon 100 bps
    standard_coupon = 0.01

    # Quoted par spread 120 bps
    quoted_par_spread = 0.0120

    upfront = isda_upfront_charge(
        valuation_date,
        effective_date,
        maturity_date,
        quoted_par_spread,
        standard_coupon,
        curve,
        recovery_rate,
        notional,
    )

    # The upfront charge should be roughly positive (protection buyer pays upfront)
    # since par spread (120 bps) > standard coupon (100 bps)
    assert upfront > 0

    # Convert back to par spread
    implied_par = isda_par_spread(
        valuation_date,
        effective_date,
        maturity_date,
        upfront,
        standard_coupon,
        curve,
        recovery_rate,
        notional,
    )

    assert implied_par == pytest.approx(quoted_par_spread, rel=1e-5)
