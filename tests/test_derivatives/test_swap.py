"""Unit tests for Interest Rate Swaps."""

import numpy as np
import pytest

from src.curve.nelson_siegel import NelsonSiegelCurve
from src.derivatives.swap import InterestRateSwap, swap_pv, swap_rate


def test_swap_rate_flat_curve():
    # A flat curve at 5% continuous
    curve = NelsonSiegelCurve(beta0=0.05, beta1=0.0, beta2=0.0, tau=1.0)
    # 5-year swap, semi-annual payments
    swap = InterestRateSwap(notional=1e6, fixed_rate=0.0, tenor=5.0, freq=2)

    s_rate = swap_rate(swap, curve)
    # For a flat continuous rate of r, the discrete rate per period compounded is:
    # (1 + R/m)^m = e^r => R = m * (e^{r/m} - 1)
    # For r=0.05, m=2: R = 2 * (e^{0.025} - 1) = 0.050629
    expected_rate = 2 * (np.exp(0.05 / 2) - 1)
    assert s_rate == pytest.approx(expected_rate, rel=1e-5)


def test_swap_pv_par_swap():
    curve = NelsonSiegelCurve(beta0=0.05, beta1=0.0, beta2=0.0, tau=1.0)
    # Create a swap with fixed rate = par rate
    s_rate = 2 * (np.exp(0.05 / 2) - 1)
    swap = InterestRateSwap(notional=1000000.0, fixed_rate=s_rate, tenor=5.0, freq=2)

    pv_receiver = swap_pv(swap, curve, position="receiver")
    pv_payer = swap_pv(swap, curve, position="payer")

    assert pv_receiver == pytest.approx(0.0, abs=1e-4)
    assert pv_payer == pytest.approx(0.0, abs=1e-4)


def test_swap_pv_off_market():
    curve = NelsonSiegelCurve(beta0=0.05, beta1=0.0, beta2=0.0, tau=1.0)
    # Par rate is ~5.06%
    # Fixed rate is 6% -> Receiver swap is in the money (PV > 0)
    swap = InterestRateSwap(notional=1000000.0, fixed_rate=0.06, tenor=5.0, freq=2)

    pv_receiver = swap_pv(swap, curve, position="receiver")
    pv_payer = swap_pv(swap, curve, position="payer")

    assert pv_receiver > 0.0
    assert pv_payer < 0.0
    assert pv_receiver == pytest.approx(-pv_payer, rel=1e-5)
