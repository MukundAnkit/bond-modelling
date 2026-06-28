"""Tests for the bootstrapping algorithm."""

import numpy as np
import pytest

from src.bootstrap.bootstrap import bootstrap_spot_rates

# ---------------------------------------------------------------------------
# Annual frequency (freq=1)
# ---------------------------------------------------------------------------


def test_flat_yield_curve() -> None:
    maturities = np.array([1.0, 2.0, 3.0, 5.0, 7.0, 10.0])
    par_yields = np.full_like(maturities, 0.05)
    spot = bootstrap_spot_rates(maturities, par_yields, freq=1)
    assert np.allclose(spot, 0.05, atol=1e-10)


def test_single_maturity() -> None:
    maturities = np.array([1.0])
    par_yields = np.array([0.04])
    spot = bootstrap_spot_rates(maturities, par_yields, freq=1)
    assert spot[0] == pytest.approx(0.04, abs=1e-12)


def test_two_maturity_upward_sloping() -> None:
    maturities = np.array([1.0, 2.0])
    par_yields = np.array([0.04, 0.05])
    spot = bootstrap_spot_rates(maturities, par_yields, freq=1)
    assert spot[0] == pytest.approx(0.04, abs=1e-12)
    assert spot[1] > 0.05


def test_two_maturity_downward_sloping() -> None:
    maturities = np.array([1.0, 2.0])
    par_yields = np.array([0.05, 0.04])
    spot = bootstrap_spot_rates(maturities, par_yields, freq=1)
    assert spot[0] == pytest.approx(0.05, abs=1e-12)
    assert spot[1] < 0.04


def test_three_maturity_spot_progression() -> None:
    maturities = np.array([1.0, 2.0, 3.0])
    par_yields = np.array([0.04, 0.05, 0.06])
    spot = bootstrap_spot_rates(maturities, par_yields, freq=1)
    assert spot[0] == pytest.approx(0.04, abs=1e-12)
    assert spot[1] > spot[0]
    assert spot[2] > spot[1]


def test_bootstrap_known_spot_two_year() -> None:
    maturities = np.array([1.0, 2.0])
    par_yields = np.array([0.04, 0.05])
    spot = bootstrap_spot_rates(maturities, par_yields, freq=1)
    c2 = 0.05
    pv_coupon = c2 * 100.0 / (1.0 + spot[0])
    remaining = 100.0 - pv_coupon
    expected_spot2 = ((100.0 * c2 + 100.0) / remaining) ** (1.0 / 2.0) - 1.0
    assert spot[1] == pytest.approx(expected_spot2, abs=1e-12)


def test_bootstrap_five_maturity() -> None:
    maturities = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    par_yields = np.array([0.03, 0.035, 0.04, 0.045, 0.05])
    spot = bootstrap_spot_rates(maturities, par_yields, freq=1)
    assert len(spot) == 5
    assert np.all(np.diff(spot) > 0)


def test_zero_coupon_curve() -> None:
    maturities = np.array([1.0, 2.0, 3.0, 5.0])
    par_yields = np.zeros(4)
    spot = bootstrap_spot_rates(maturities, par_yields, freq=1)
    assert np.allclose(spot, 0.0, atol=1e-12)


def test_negative_par_yields() -> None:
    maturities = np.array([1.0, 2.0, 3.0])
    par_yields = np.array([-0.005, -0.003, 0.0])
    spot = bootstrap_spot_rates(maturities, par_yields, freq=1)
    assert np.all(np.isfinite(spot))


def test_bootstrap_output_shape() -> None:
    maturities = np.array([1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0])
    par_yields = np.linspace(0.04, 0.06, 8)
    spot = bootstrap_spot_rates(maturities, par_yields, freq=1)
    assert spot.shape == maturities.shape


def test_invalid_maturities_non_increasing() -> None:
    maturities = np.array([1.0, 3.0, 2.0])
    par_yields = np.array([0.04, 0.05, 0.045])
    with pytest.raises(ValueError, match="increasing"):
        bootstrap_spot_rates(maturities, par_yields, freq=1)


def test_invalid_maturities_negative() -> None:
    maturities = np.array([-1.0, 2.0])
    par_yields = np.array([0.04, 0.05])
    with pytest.raises(ValueError, match="positive"):
        bootstrap_spot_rates(maturities, par_yields, freq=1)


def test_invalid_freq() -> None:
    maturities = np.array([1.0, 2.0])
    par_yields = np.array([0.04, 0.05])
    with pytest.raises(ValueError, match="freq"):
        bootstrap_spot_rates(maturities, par_yields, freq=3)


def test_mismatched_lengths() -> None:
    maturities = np.array([1.0, 2.0, 3.0])
    par_yields = np.array([0.04, 0.05])
    with pytest.raises(ValueError, match="same length"):
        bootstrap_spot_rates(maturities, par_yields, freq=1)


# ---------------------------------------------------------------------------
# Semi-annual frequency (freq=2)
# ---------------------------------------------------------------------------


def test_semi_flat_yield_curve() -> None:
    maturities = np.array([1.0, 2.0, 3.0, 5.0])
    par_yields = np.full_like(maturities, 0.06)
    spot = bootstrap_spot_rates(maturities, par_yields, freq=2)
    assert spot[0] == pytest.approx(0.06, abs=1e-12)
    assert np.all(np.isfinite(spot))
    assert np.all(spot > 0.0)


def test_semi_two_maturity_known_value() -> None:
    maturities = np.array([1.0, 2.0])
    par_yields = np.array([0.04, 0.05])
    spot = bootstrap_spot_rates(maturities, par_yields, freq=2)
    assert len(spot) == 2
    assert spot[0] == pytest.approx(0.04, abs=1e-12)
    c2 = 0.05
    coupon = 100.0 * c2 / 2
    df_half = 1.0 / (1.0 + spot[0]) ** 0.5
    df_one = 1.0 / (1.0 + spot[0]) ** 1.0
    df_1_5 = 1.0 / (1.0 + spot[0]) ** 1.5
    pv_known = coupon * (df_half + df_one + df_1_5)
    remaining = 100.0 - pv_known
    expected_spot2 = ((coupon + 100.0) / remaining) ** (1.0 / 2.0) - 1.0
    assert spot[1] == pytest.approx(expected_spot2, abs=1e-12)


def test_semi_invalid_maturities_below_05() -> None:
    maturities = np.array([0.25, 1.0])
    par_yields = np.array([0.03, 0.04])
    with pytest.raises(ValueError, match="0.5"):
        bootstrap_spot_rates(maturities, par_yields, freq=2)


def test_semi_three_maturity_progression() -> None:
    maturities = np.array([1.0, 2.0, 3.0])
    par_yields = np.array([0.04, 0.05, 0.055])
    spot = bootstrap_spot_rates(maturities, par_yields, freq=2)
    assert len(spot) == 3
    assert spot[0] == pytest.approx(0.04, abs=1e-12)
    assert np.all(np.diff(spot) > 0)
