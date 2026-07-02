"""Unit tests for Reduced Form Models."""

import numpy as np
import pytest

from src.credit.reduced_form import (
    constant_hazard_survival,
    jarrow_turnbull_price,
    piecewise_hazard_survival,
)


def test_constant_hazard_survival():
    lam = 0.05  # 5% default intensity

    t = 2.0
    s = constant_hazard_survival(lam, t)

    assert s == pytest.approx(np.exp(-0.05 * 2.0))


def test_piecewise_hazard_survival():
    # lam = 0.05 for [0, 1), 0.08 for [1, 3), 0.10 for [3, inf)
    hazard_rates = [0.05, 0.08, 0.10]
    times = [1.0, 3.0, 10.0]

    s_0_5 = piecewise_hazard_survival(hazard_rates, times, 0.5)
    assert s_0_5 == pytest.approx(np.exp(-0.05 * 0.5))

    s_2_0 = piecewise_hazard_survival(hazard_rates, times, 2.0)
    assert s_2_0 == pytest.approx(np.exp(-0.05 * 1.0 - 0.08 * 1.0))

    s_4_0 = piecewise_hazard_survival(hazard_rates, times, 4.0)
    assert s_4_0 == pytest.approx(np.exp(-0.05 * 1.0 - 0.08 * 2.0 - 0.10 * 1.0))


def test_jarrow_turnbull_price():
    # Jarrow-Turnbull simplified pricing for a zero-coupon corporate bond
    # Price = Exp(-r * T) * (Recovery + (1 - Recovery) * Survival(T))
    r = 0.04
    lam = 0.05
    t_mat = 5.0
    rec_rate = 0.40

    def curve(_):
        return r

    def survival(t):
        return constant_hazard_survival(lam, t)

    price = jarrow_turnbull_price(curve, survival, rec_rate, t_mat)

    expected_price = np.exp(-0.04 * 5.0) * (0.40 + 0.60 * np.exp(-0.05 * 5.0))

    assert price == pytest.approx(expected_price)
