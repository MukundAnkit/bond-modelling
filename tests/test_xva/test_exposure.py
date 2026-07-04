# ruff: noqa
import numpy as np
from xva.exposure import simulate_exposures


def test_simulate_exposures():
    mtm_paths = np.array([[10.0, -5.0, 20.0], [-10.0, 5.0, 30.0], [0.0, 0.0, -10.0]])
    ee, pfe, ene = simulate_exposures(mtm_paths)

    # ee at t=0: mean(10, 0, 0) = 3.333
    np.testing.assert_almost_equal(ee[0], 10 / 3)
    # ee at t=1: mean(0, 5, 0) = 1.666
    np.testing.assert_almost_equal(ee[1], 5 / 3)
    # ee at t=2: mean(20, 30, 0) = 50/3 = 16.666
    np.testing.assert_almost_equal(ee[2], 50 / 3)

    # ene at t=0: mean(0, -10, 0) = -3.333
    np.testing.assert_almost_equal(ene[0], -10 / 3)
    # ene at t=1: mean(-5, 0, 0) = -1.666
    np.testing.assert_almost_equal(ene[1], -5 / 3)
    # ene at t=2: mean(0, 0, -10) = -3.333
    np.testing.assert_almost_equal(ene[2], -10 / 3)

    assert pfe.shape == (3,)
    assert np.all(pfe >= ee)


def test_simulate_exposures_with_margin():
    mtm_paths = np.array([[10.0, 20.0, -10.0, 30.0], [5.0, 15.0, 5.0, 25.0]])
    im_paths = np.array([[2.0, 2.0, 2.0, 2.0], [1.0, 1.0, 1.0, 1.0]])

    ee, pfe, ene = simulate_exposures(mtm_paths, mpor_steps=1, im_paths=im_paths)
    np.testing.assert_almost_equal(ee, [6.0, 8.5, 0.0, 28.5])
    np.testing.assert_almost_equal(ene, [0.0, 0.0, -20.0, 0.0])
