import numpy as np

from src.trees.hull_white import HullWhite1F


def test_hull_white_zcb():
    f = 0.05

    def curve(_t):
        return f

    a = 0.1
    sigma = 0.01
    model = HullWhite1F(a, sigma, curve)

    t_end = 5.0
    p_0_t = 1.0
    p_0_end = np.exp(-f * t_end)

    zcb_price = model.zero_coupon_bond(0.0, t_end, r_t=f, p_0_t=p_0_t, p_0_end=p_0_end)
    assert np.isclose(zcb_price, p_0_end, atol=1e-4)

    b_val = model.b_factor(0, t_end)
    assert np.isclose(b_val, (1 - np.exp(-a * t_end)) / a)
