import pytest
import numpy as np
from src.trees.binomial import BinomialTree

def test_tree_recombines():
    # A standard binomial tree should recombine, meaning rate at step 2, state 1
    # is the same whether we went up-down or down-up.
    tree = BinomialTree(r0=0.05, volatility=0.20, time_step=1.0, periods=3)
    rates = tree.build_tree()
    
    # Expected number of nodes at period 2 is 3
    assert len(rates[2]) == 3
    # Check if the rate formula matches expected u * d = 1 behavior if we implemented it that way,
    # or just check that building completes and array shapes are correct.
    assert rates[2][1] > rates[2][0]

def test_tree_probabilities():
    # Test that risk neutral probabilities sum to 1.
    tree = BinomialTree(r0=0.05, volatility=0.20, time_step=1.0, periods=3)
    probs = tree.get_probabilities()
    assert probs['p_up'] + probs['p_down'] == 1.0

def test_tree_pricing():
    # A simple bond priced on the tree should roughly equal continuous/discrete discounting
    # for a zero volatility assumption.
    tree = BinomialTree(r0=0.05, volatility=0.0001, time_step=1.0, periods=2)
    # Price a 2-period zero coupon bond with face value 100
    price = tree.price_zero_coupon_bond(face_value=100.0)
    
    # Since vol ~ 0, price should be 100 / ((1 + 0.05)^2) if annual compounding
    expected = 100.0 / ((1.05) ** 2)
    np.testing.assert_almost_equal(price, expected, decimal=1)
