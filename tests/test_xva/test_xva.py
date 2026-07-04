# ruff: noqa
import numpy as np
from xva.xva import (
    calculate_cva,
    calculate_dva,
    calculate_fva,
    calculate_cva_wwr,
    calculate_kva,
)


def test_calculate_cva():
    ee = np.array([10.0, 20.0, 30.0])
    pd = np.array([0.01, 0.01, 0.02])
    lgd = 0.5
    df = np.array([1.0, 0.95, 0.9])

    cva = calculate_cva(ee, pd, lgd, df)
    # 0.5 * (10*0.01*1.0 + 20*0.01*0.95 + 30*0.02*0.9)
    # 0.5 * (0.1 + 0.19 + 0.54) = 0.5 * 0.83 = 0.415
    np.testing.assert_almost_equal(cva, 0.415)


def test_calculate_dva():
    ene = np.array([-5.0, -10.0, -15.0])
    pd_own = np.array([0.01, 0.02, 0.02])
    lgd_own = 0.4
    df = np.array([1.0, 0.95, 0.9])

    dva = calculate_dva(ene, pd_own, lgd_own, df)
    # 0.4 * (5*0.01*1.0 + 10*0.02*0.95 + 15*0.02*0.9)
    # 0.4 * (0.05 + 0.19 + 0.27) = 0.4 * 0.51 = 0.204
    np.testing.assert_almost_equal(dva, 0.204)


def test_calculate_fva():
    ee = np.array([10.0, 20.0, 30.0])
    ene = np.array([-5.0, -10.0, -15.0])
    fca_spread = 0.015
    fba_spread = 0.010
    df = np.array([1.0, 0.95, 0.9])
    dt = 1.0

    fva = calculate_fva(ee, ene, fca_spread, fba_spread, df, dt)
    # fca = 0.015 * (10*1.0 + 20*0.95 + 30*0.9) * 1.0 = 0.015 * (10 + 19 + 27) = 0.015 * 56 = 0.84
    # fba = 0.010 * (5*1.0 + 10*0.95 + 15*0.9) * 1.0 = 0.010 * (5 + 9.5 + 13.5) = 0.010 * 28 = 0.28
    # fva = 0.84 - 0.28 = 0.56
    np.testing.assert_almost_equal(fva, 0.56)


def test_calculate_cva_wwr():
    exposure_paths = np.array([[10.0, 20.0], [20.0, 30.0], [30.0, 10.0]])
    pd_marginal = np.array([0.01, 0.02])
    lgd = 0.5
    df = np.array([1.0, 0.9])

    cva_wwr = calculate_cva_wwr(exposure_paths, pd_marginal, lgd, df, 0.5)
    assert cva_wwr > 0

    # With 0 correlation it should match normal CVA
    cva_no_wwr = calculate_cva_wwr(exposure_paths, pd_marginal, lgd, df, 0.0)
    cva_standard = calculate_cva(np.mean(exposure_paths, axis=0), pd_marginal, lgd, df)
    np.testing.assert_almost_equal(cva_no_wwr, cva_standard)


def test_calculate_kva():
    capital_paths = np.array([100.0, 80.0, 60.0])
    cost_of_capital = 0.10
    df = np.array([1.0, 0.95, 0.9])
    dt = 1.0
    kva = calculate_kva(capital_paths, cost_of_capital, df, dt)
    # kva = 0.10 * (100*1.0 + 80*0.95 + 60*0.9) = 23.0
    np.testing.assert_almost_equal(kva, 23.0)
