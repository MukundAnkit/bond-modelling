"""Unit tests for Monotone Convex Spline (Hagan-West)."""

import numpy as np
import pytest

from src.curve.hagan_west import MonotoneConvexSpline


def test_hagan_west_initialization():
    times = np.array([0.0, 1.0, 2.0, 3.0])
    discrete_forwards = np.array([0.02, 0.03, 0.04])
    
    spline = MonotoneConvexSpline(times, discrete_forwards)
    assert spline.t.shape[0] == 4
    assert spline.F.shape[0] == 3


def test_hagan_west_positivity():
    times = np.array([0.0, 1.0, 2.0])
    # A negative forward might be enforced locally to 0 by positivity constraint
    discrete_forwards = np.array([0.02, -0.01])
    
    spline = MonotoneConvexSpline(times, discrete_forwards)
    # The instantaneous rates should be non-negative
    f_vals = spline(np.linspace(0, 2, 10))
    for f in f_vals:
        assert f >= 0.0


def test_hagan_west_discount_factor():
    times = np.array([0.0, 1.0, 2.0])
    discrete_forwards = np.array([0.02, 0.03])
    
    spline = MonotoneConvexSpline(times, discrete_forwards)
    df = spline.discount_factor(1.0)
    assert 0.0 < df < 1.0
