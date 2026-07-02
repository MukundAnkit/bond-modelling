# ruff: noqa
import numpy as np
from src.structured.copula import (
    GaussianCopula,
    StudentTCopula,
    default_times_from_copula,
)


def test_gaussian_copula():
    corr = np.array([[1.0, 0.5], [0.5, 1.0]])
    copula = GaussianCopula(corr)
    u = copula.simulate(1000, seed=42)
    assert u.shape == (1000, 2)
    assert np.all((u >= 0) & (u <= 1))


def test_student_t_copula():
    corr = np.array([[1.0, 0.5], [0.5, 1.0]])
    copula = StudentTCopula(corr, df=4.0)
    u = copula.simulate(1000, seed=42)
    assert u.shape == (1000, 2)
    assert np.all((u >= 0) & (u <= 1))


def test_default_times():
    u = np.array([[0.1, 0.9], [0.5, 0.5]])
    hr = np.array([0.01, 0.05])
    t = default_times_from_copula(u, hr)
    assert t.shape == (2, 2)
    assert np.all(t >= 0)
