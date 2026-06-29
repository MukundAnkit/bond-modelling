import numpy as np
import pandas as pd
import pytest

from src.curve.pca import YieldCurvePCA


def test_yield_curve_pca_basic():
    # Synthetic data: 100 observations, 5 maturities
    # PC1 = parallel shift (all maturities move together)
    np.random.seed(42)
    obs = 100
    mats = 5

    # Generate random level shocks (large variance)
    level_shocks = np.random.normal(0, 0.10, obs)
    # Generate random slope shocks (smaller variance)
    slope_shocks = np.random.normal(0, 0.03, obs)

    data = np.zeros((obs, mats))
    for i in range(obs):
        # parallel shift
        data[i, :] += level_shocks[i]
        # steepness (short end down, long end up)
        data[i, :] += slope_shocks[i] * np.linspace(-1, 1, mats)

    df = pd.DataFrame(data)

    pca = YieldCurvePCA(n_components=2)
    pca.fit(df)

    assert pca.components_ is not None
    assert pca.components_.shape == (2, mats)
    assert pca.explained_variance_ratio_ is not None
    assert len(pca.explained_variance_ratio_) == 2

    # PC1 should explain the vast majority of the variance (due to 0.10 vs 0.03 std devs)  # noqa: E501
    assert pca.explained_variance_ratio_[0] > 0.80
    assert np.sum(pca.explained_variance_ratio_) > 0.95


def test_pca_transform_and_inverse():
    np.random.seed(42)
    data = np.random.normal(0, 1, (50, 10))

    # Fit full PCA to perfectly reconstruct
    pca = YieldCurvePCA(n_components=10)
    pca.fit(data)

    transformed = pca.transform(data)
    assert transformed.shape == (50, 10)

    # Check orthogonality of components: dot product of different components should be ~0  # noqa: E501
    dot_prod = np.dot(pca.components_[0], pca.components_[1])
    assert pytest.approx(dot_prod, abs=1e-10) == 0.0

    # Components should be normalized (norm=1)
    norm = np.linalg.norm(pca.components_[0])
    assert pytest.approx(norm, abs=1e-10) == 1.0


def test_pca_generate_shock():
    np.random.seed(42)
    data = np.random.normal(0, 1, (50, 5))

    pca = YieldCurvePCA(n_components=3)
    pca.fit(data)

    # Shock of +1 std dev to PC1
    shock_pc1 = pca.generate_shock([1.0])

    # Should equal 1 * std_dev[0] * components[0]
    expected_shock = pca.std_devs_[0] * pca.components_[0]
    np.testing.assert_allclose(shock_pc1, expected_shock)

    # Shock combining PC1 and PC2
    shock_both = pca.generate_shock([1.0, -0.5])
    expected_both = (1.0 * pca.std_devs_[0] * pca.components_[0]) + (
        -0.5 * pca.std_devs_[1] * pca.components_[1]
    )
    np.testing.assert_allclose(shock_both, expected_both)


def test_pca_insufficient_data():
    pca = YieldCurvePCA(n_components=2)
    with pytest.raises(ValueError, match="Need at least 2 observations"):
        pca.fit(np.array([[1, 2, 3]]))
