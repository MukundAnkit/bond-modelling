"""Unit tests for Arbitrage-Free Nelson-Siegel (AFNS)."""

import numpy as np
import pytest

from src.curve.afns import ArbitrageFreeNelsonSiegel


def test_afns_initialization():
    afns = ArbitrageFreeNelsonSiegel(
        beta0=0.05, beta1=-0.02, beta2=0.01, tau=1.5, sigma=0.01
    )
    assert afns.beta0 == 0.05
    assert afns.sigma == 0.01

    with pytest.raises(ValueError):
        ArbitrageFreeNelsonSiegel(
            beta0=0.05, beta1=-0.02, beta2=0.01, tau=1.5, sigma=-0.01
        )


def test_afns_convexity_adjustment():
    afns = ArbitrageFreeNelsonSiegel(
        beta0=0.05, beta1=-0.02, beta2=0.01, tau=1.5, sigma=0.05
    )

    # Convexity adjustment at t=0 should be 0
    assert afns.convexity_adjustment(0.0) == 0.0

    # Convexity adjustment at t>0 should be positive
    assert afns.convexity_adjustment(10.0) > 0.0


def test_afns_yield_rate():
    afns = ArbitrageFreeNelsonSiegel(
        beta0=0.05, beta1=0.0, beta2=0.0, tau=1.5, sigma=0.01
    )

    y = afns.yield_rate(10.0)
    # The yield should be lower than beta0 due to convexity adjustment
    assert y < 0.05


def test_afns_fit():
    maturities = np.array([1.0, 2.0, 3.0, 5.0, 10.0])
    spot_rates = np.array([0.02, 0.025, 0.03, 0.035, 0.04])

    fitted = ArbitrageFreeNelsonSiegel.fit(maturities, spot_rates)
    assert fitted.beta0 > 0
    assert fitted.sigma >= 0
