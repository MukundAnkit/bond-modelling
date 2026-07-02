import numpy as np

from src.trees.trinomial_tree import HWTree


def test_hw_tree():
    r = 0.05

    def zero_curve(t_val):
        return np.exp(-r * t_val)

    a = 0.1
    sigma = 0.01
    dt = 1.0
    n_steps = 5

    tree = HWTree(a, sigma, dt, n_steps, zero_curve)

    assert len(tree.alpha) == n_steps + 1
    assert tree.Q[0][0] == 1.0

    for i in range(1, n_steps):
        zcb_expected = zero_curve(i * dt)
        zcb_tree = sum(tree.Q[i].values())
        assert np.isclose(zcb_expected, zcb_tree, atol=1e-4)
