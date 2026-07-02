# ruff: noqa
# mypy: ignore-errors
import numpy as np
from scipy.stats import norm, t


class Copula:
    def simulate(self, n_samples: int) -> np.ndarray:
        raise NotImplementedError


class GaussianCopula(Copula):
    def __init__(self, correlation_matrix: np.ndarray):
        self.correlation_matrix = correlation_matrix
        self.n_dim = correlation_matrix.shape[0]
        self.cholesky = np.linalg.cholesky(correlation_matrix)

    def simulate(self, n_samples: int, seed: int | None = None) -> np.ndarray:
        if seed is not None:
            np.random.seed(seed)
        Z = np.random.standard_normal((n_samples, self.n_dim))
        X = Z @ self.cholesky.T
        U = norm.cdf(X)
        return U


class StudentTCopula(Copula):
    def __init__(self, correlation_matrix: np.ndarray, df: float):
        self.correlation_matrix = correlation_matrix
        self.df = df
        self.n_dim = correlation_matrix.shape[0]
        self.cholesky = np.linalg.cholesky(correlation_matrix)

    def simulate(self, n_samples: int, seed: int | None = None) -> np.ndarray:
        if seed is not None:
            np.random.seed(seed)
        Z = np.random.standard_normal((n_samples, self.n_dim))
        X = Z @ self.cholesky.T
        chi2 = np.random.chisquare(self.df, size=(n_samples, 1))
        W = np.sqrt(self.df / chi2)
        T_vars = X * W
        U = t.cdf(T_vars, df=self.df)
        return U


def default_times_from_copula(u: np.ndarray, hazard_rates: np.ndarray) -> np.ndarray:
    """
    Map uniform variables from copula to default times assuming constant hazard rates.
    """
    return -np.log(1 - u) / hazard_rates
