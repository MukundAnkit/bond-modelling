# ruff: noqa
import numpy as np
from src.exotics.cms import ConstantMaturitySwap


def test_cms_convexity_adjustment():
    S0 = 0.05
    tenor = 10.0
    freq = 2.0
    vol = 0.20
    cms = ConstantMaturitySwap(S0, tenor, freq, vol)

    ca = cms.convexity_adjustment(time_to_fixing=5.0)
    assert ca > 0  # Convexity adjustment is typically positive
    assert ca < 0.01  # Should be a small number

    adjusted = cms.adjusted_rate(time_to_fixing=5.0)
    assert adjusted > S0
