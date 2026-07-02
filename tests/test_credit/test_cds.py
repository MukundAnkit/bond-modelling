"""Unit tests for Credit Default Swaps (CDS)."""

import numpy as np
import pytest

from src.credit.cds import CDS, cds_par_spread, cds_premium_leg, cds_protection_leg


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
