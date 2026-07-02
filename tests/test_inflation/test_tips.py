import numpy as np
import pytest

from src.inflation.tips import TIPS


def test_tips_initialization():
    tips = TIPS(
        face_value=100.0, coupon_rate=0.02, maturity=2.0, freq=2, base_cpi=250.0
    )
    assert tips.base_cpi == 250.0
    assert tips.periods == 4
    assert tips.coupon_payment == 1.0

    with pytest.raises(ValueError):
        TIPS(face_value=100.0, coupon_rate=0.02, maturity=2.0, freq=2, base_cpi=-10.0)


def test_tips_inflation_adjusted_cashflows():
    tips = TIPS(
        face_value=100.0, coupon_rate=0.02, maturity=1.0, freq=2, base_cpi=100.0
    )

    # index ratios for 2 periods
    index_ratios = np.array([1.02, 1.05])
    t, adjusted_cf = tips.inflation_adjusted_cashflows(index_ratios)

    np.testing.assert_array_equal(t, [1, 2])
    # Period 1: 1.0 * 1.02 = 1.02
    # Period 2: 1.0 * 1.05 + 100.0 * 1.05 = 106.05
    np.testing.assert_allclose(adjusted_cf, [1.02, 106.05])


def test_tips_deflation_floor():
    tips = TIPS(
        face_value=100.0, coupon_rate=0.02, maturity=1.0, freq=2, base_cpi=100.0
    )

    # index ratios for 2 periods, showing deflation
    index_ratios = np.array([0.98, 0.95])
    t, adjusted_cf = tips.inflation_adjusted_cashflows(index_ratios)

    # Period 1: 1.0 * 0.98 = 0.98
    # Period 2: 1.0 * 0.95 + 100.0 * max(1.0, 0.95) = 0.95 + 100.0 = 100.95
    np.testing.assert_allclose(adjusted_cf, [0.98, 100.95])
