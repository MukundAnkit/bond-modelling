import numpy as np

from src.trees.bermudan import BermudanSwaption
from src.trees.hull_white import HullWhite1F
from src.trees.trinomial_tree import HWTree


def test_bermudan_swaption():
    r = 0.05

    def zero_curve(t_val):
        return np.exp(-r * t_val)

    def fwd_curve(_t):
        return r

    a = 0.1
    sigma = 0.01
    dt = 0.5
    n_steps = 10

    hw_model = HullWhite1F(a, sigma, fwd_curve)
    tree = HWTree(a, sigma, dt, n_steps, zero_curve)

    strike = 0.05
    exercise_times = [1.0, 2.0, 3.0, 4.0]
    swap_payment_times = [1.0, 2.0, 3.0, 4.0, 5.0]

    swaption = BermudanSwaption(
        hw_model, tree, strike, exercise_times, swap_payment_times, is_payer=True
    )
    price = swaption.price()

    assert price >= 0.0
    assert price < 0.1
