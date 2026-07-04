"""Unit tests for Global Multi-Curve Solver."""

import numpy as np
import pytest

from src.bootstrap.multicurve import MultiCurveSolver


def test_multicurve_solver_initialization():
    ois_mats = np.array([1.0, 2.0])
    ois_rates = np.array([0.02, 0.03])
    irs_mats = np.array([1.0, 2.0])
    irs_rates = np.array([0.025, 0.035])
    
    solver = MultiCurveSolver(ois_mats, ois_rates, irs_mats, irs_rates)
    assert solver.n_ois == 2
    assert solver.n_irs == 2


def test_multicurve_solver_solve():
    ois_mats = np.array([1.0, 2.0, 3.0])
    ois_rates = np.array([0.01, 0.015, 0.02])
    irs_mats = np.array([1.0, 2.0, 3.0])
    irs_rates = np.array([0.012, 0.018, 0.025])
    
    solver = MultiCurveSolver(ois_mats, ois_rates, irs_mats, irs_rates)
    ois_zeros, irs_zeros = solver.solve()
    
    assert len(ois_zeros) == 3
    assert len(irs_zeros) == 3
    
    # Check that pricing error is near zero
    errors = solver._pricing_error(np.concatenate([ois_zeros, irs_zeros]))
    assert np.linalg.norm(errors, ord=np.inf) < 1e-5
