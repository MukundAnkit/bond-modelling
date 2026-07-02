import numpy as np
import pytest

from src.inflation.curves import bootstrap_real_rates, breakeven_inflation


def test_bootstrap_real_rates():
    maturities = np.array([1.0, 2.0])
    par_yields = np.array([0.01, 0.015])

    # Should work identically to nominal bootstrapping
    spots = bootstrap_real_rates(maturities, par_yields, freq=1)

    # Check that it returns spots
    assert len(spots) == 2
    assert spots[0] == 0.01
    assert spots[1] > 0.015


def test_breakeven_inflation():
    nominal_spots = np.array([0.04, 0.045])
    real_spots = np.array([0.01, 0.015])

    breakevens = breakeven_inflation(nominal_spots, real_spots)

    expected_1 = (1.04 / 1.01) - 1.0
    expected_2 = (1.045 / 1.015) - 1.0

    np.testing.assert_allclose(breakevens, [expected_1, expected_2])


def test_breakeven_inflation_mismatch():
    with pytest.raises(ValueError):
        breakeven_inflation(np.array([0.04]), np.array([0.01, 0.02]))
