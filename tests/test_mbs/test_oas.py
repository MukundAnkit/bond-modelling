import numpy as np

from mbs.oas import calculate_oas, generate_hw1f_paths, price_mbs
from mbs.pass_through import project_cash_flows


def test_generate_hw1f_paths():
    paths = generate_hw1f_paths(0.05, 0.1, 0.01, 10, 120, 1.0 / 12.0, 0.05)
    assert paths.shape == (10, 120)
    assert np.allclose(paths[:, 0], 0.05)


def test_price_mbs():
    cash_flows = np.array([100.0, 100.0, 100.0])
    rate_path = np.array([0.05, 0.05, 0.05])
    oas = 0.01
    price = price_mbs(cash_flows, rate_path, oas)
    expected = 100 / 1.005 + 100 / (1.005**2) + 100 / (1.005**3)
    assert np.isclose(price, expected)


def test_calculate_oas():
    balance = 1000.0
    wac = 0.05
    term = 12
    rate_paths = np.full((5, term), 0.04)

    def dummy_prepay(_rate_path, _wac):
        return lambda t, pf: 0.0

    cf = project_cash_flows(balance, wac, term, np.zeros(term))["total_cash_flow"]
    expected_oas = 0.015
    price = price_mbs(cf, rate_paths[0], expected_oas)

    calc_oas = calculate_oas(price, balance, wac, term, rate_paths, dummy_prepay)
    assert np.isclose(calc_oas, expected_oas, atol=1e-4)
