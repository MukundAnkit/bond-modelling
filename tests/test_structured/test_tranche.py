# ruff: noqa
import numpy as np
import pytest
from src.structured.tranche import Tranche


def test_tranche_loss():
    equity = Tranche(0.0, 0.03, "Equity")
    mezz = Tranche(0.03, 0.07, "Mezzanine")
    senior = Tranche(0.07, 1.0, "Senior")

    pool_losses = np.array([0.0, 0.02, 0.05, 0.10])

    eq_loss = equity.calculate_loss(pool_losses)
    np.testing.assert_allclose(eq_loss, [0.0, 2 / 3, 1.0, 1.0])

    mezz_loss = mezz.calculate_loss(pool_losses)
    np.testing.assert_allclose(mezz_loss, [0.0, 0.0, 2 / 4, 1.0])

    senior_loss = senior.calculate_loss(pool_losses)
    np.testing.assert_allclose(senior_loss, [0.0, 0.0, 0.0, 0.03 / 0.93])


def test_invalid_tranche():
    with pytest.raises(ValueError):
        Tranche(0.05, 0.04)
