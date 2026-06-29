import numpy as np  # noqa: D100
import pandas as pd


class YieldCurvePCA:
    """Principal Component Analysis for yield curve dynamics.

    Decomposes historical yield curve changes into latent factors:
    typically Level (PC1), Steepness (PC2), and Curvature (PC3).
    """

    def __init__(self, n_components: int = 3):  # noqa: D107
        self.n_components = n_components
        self.components_: np.ndarray | None = None
        self.explained_variance_ratio_: np.ndarray | None = None
        self.mean_: np.ndarray | None = None
        self.std_devs_: np.ndarray | None = None

    def fit(self, X: pd.DataFrame | np.ndarray) -> "YieldCurvePCA":  # noqa: N803
        """Fit the PCA model to the historical yield curve data.

        Args:
            X: Historical yields. Rows are observations (dates), columns are maturities.
               Can be raw yields or daily changes (differences).
        """  # noqa: D413
        if isinstance(X, pd.DataFrame):  # noqa: SIM108
            data = X.values
        else:
            data = X

        if data.shape[0] < 2:
            raise ValueError("Need at least 2 observations to compute PCA.")

        # Center the data
        self.mean_ = np.mean(data, axis=0)
        centered_data = data - self.mean_

        # Compute SVD on centered data
        U, S, Vh = np.linalg.svd(centered_data, full_matrices=False)  # noqa: N806

        # Variances of the principal components
        variances = (S**2) / (data.shape[0] - 1)
        total_variance = np.sum(variances)

        # Store attributes
        self.explained_variance_ratio_ = variances[: self.n_components] / total_variance
        self.std_devs_ = np.sqrt(variances[: self.n_components])
        self.components_ = Vh[: self.n_components]

        # Enforce deterministic sign for components (like scikit-learn does)
        # We ensure the largest absolute value in each component is positive.
        for i in range(self.n_components):
            max_idx = np.argmax(np.abs(self.components_[i]))
            if self.components_[i, max_idx] < 0:
                self.components_[i] *= -1

        return self

    def transform(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:  # noqa: N803
        """Apply dimensionality reduction to X."""
        if self.mean_ is None or self.components_ is None:
            raise RuntimeError("Model is not fitted yet. Call fit() first.")

        if isinstance(X, pd.DataFrame):  # noqa: SIM108
            data = X.values
        else:
            data = X

        centered_data = data - self.mean_
        return np.dot(centered_data, self.components_.T)  # type: ignore

    def generate_shock(self, std_shocks: list[float]) -> np.ndarray:
        """Generate a curve shock vector by applying standard deviation shocks to the PCs.

        Args:
            std_shocks: List of shocks in standard deviations.
                        E.g., [1.0, 0.0, 0.0] represents a +1 std dev shock to PC1 (Level).

        Returns:
            np.ndarray: The resulting shock vector (same length as the original maturities).
        """  # noqa: D413, E501
        if self.components_ is None or self.std_devs_ is None:
            raise RuntimeError("Model is not fitted yet. Call fit() first.")

        if len(std_shocks) > self.n_components:
            raise ValueError(
                f"Expected at most {self.n_components} shocks, got {len(std_shocks)}"
            )

        # Start with a zero shock vector
        shock = np.zeros_like(self.mean_)

        for i, shock_stdev in enumerate(std_shocks):
            # The actual magnitude of a 1 std dev move in component i
            shock += shock_stdev * self.std_devs_[i] * self.components_[i]

        return shock
