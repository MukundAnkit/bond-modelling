"""Tests for discount-factor interpolation."""

import numpy as np
import pytest

from src.bootstrap.interpolate import interpolate_df


def test_interpolate_exact_match() -> None:
    maturities = np.array([1.0, 3.0, 5.0])
    spot_rates = np.array([0.04, 0.05, 0.06])
    for t, z in zip(maturities, spot_rates, strict=True):
        expected = 1.0 / (1.0 + z) ** t
        result = interpolate_df(t, maturities, spot_rates)
        assert result == pytest.approx(expected, abs=1e-12)


def test_interpolate_between() -> None:
    maturities = np.array([1.0, 5.0])
    spot_rates = np.array([0.04, 0.06])
    df_1 = 1.0 / (1.0 + 0.04) ** 1.0
    df_5 = 1.0 / (1.0 + 0.06) ** 5.0
    t = 3.0
    ln_df = np.log(df_1) + (np.log(df_5) - np.log(df_1)) * (t - 1.0) / (5.0 - 1.0)
    expected = np.exp(ln_df)
    result = interpolate_df(t, maturities, spot_rates)
    assert result == pytest.approx(float(expected), abs=1e-12)


def test_interpolate_forward_fill_short() -> None:
    maturities = np.array([2.0, 5.0])
    spot_rates = np.array([0.05, 0.06])
    expected = 1.0 / (1.0 + 0.05) ** 1.0
    result = interpolate_df(1.0, maturities, spot_rates)
    assert result == pytest.approx(expected, abs=1e-12)


def test_interpolate_forward_fill_long() -> None:
    maturities = np.array([2.0, 5.0])
    spot_rates = np.array([0.05, 0.06])
    expected = 1.0 / (1.0 + 0.06) ** 7.0
    result = interpolate_df(7.0, maturities, spot_rates)
    assert result == pytest.approx(expected, abs=1e-12)


def test_interpolate_single_point() -> None:
    maturities = np.array([3.0])
    spot_rates = np.array([0.05])
    for t in [1.0, 3.0, 5.0]:
        expected = 1.0 / (1.0 + 0.05) ** t
        result = interpolate_df(t, maturities, spot_rates)
        assert result == pytest.approx(expected, abs=1e-12)


def test_interpolate_monotonic() -> None:
    maturities = np.array([1.0, 2.0, 3.0, 5.0, 7.0, 10.0])
    spot_rates = np.array([0.03, 0.035, 0.04, 0.045, 0.05, 0.055])
    times = np.linspace(0.5, 10.0, 50)
    dfs = [interpolate_df(float(t), maturities, spot_rates) for t in times]
    for i in range(len(dfs) - 1):
        assert dfs[i] >= dfs[i + 1] - 1e-14


def test_interpolate_negative_spot() -> None:
    maturities = np.array([1.0, 3.0])
    spot_rates = np.array([-0.01, 0.02])
    df_1 = 1.0 / (1.0 - 0.01) ** 1.0
    df_3 = 1.0 / (1.0 + 0.02) ** 3.0
    t = 2.0
    ln_df = np.log(df_1) + (np.log(df_3) - np.log(df_1)) * (t - 1.0) / (3.0 - 1.0)
    expected = np.exp(ln_df)
    result = interpolate_df(t, maturities, spot_rates)
    assert result == pytest.approx(float(expected), abs=1e-12)


def test_interpolate_single_point_forward_fill() -> None:
    maturities = np.array([5.0])
    spot_rates = np.array([0.05])
    for t in [1.0, 5.0, 10.0]:
        result = interpolate_df(t, maturities, spot_rates)
        expected = 1.0 / (1.0 + 0.05) ** t
        assert result == pytest.approx(expected, abs=1e-12)
