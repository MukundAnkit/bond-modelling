import numpy as np

from mbs.pass_through import average_life, calculate_scheduled_pmt, project_cash_flows


def test_calculate_scheduled_pmt():
    balance = 100000
    rate = 0.06 / 12
    term = 360
    pmt = calculate_scheduled_pmt(balance, rate, term)
    assert np.isclose(pmt, 599.55, atol=0.01)


def test_project_cash_flows_no_prepayment():
    balance = 100000
    wac = 0.06
    term = 360
    smm_vector = np.zeros(term)

    cf = project_cash_flows(balance, wac, term, smm_vector)
    assert np.isclose(cf["balance"][-1], 0, atol=0.01)
    assert np.allclose(cf["prepayment"], 0)

    total_cf = np.sum(cf["total_cash_flow"])
    pmt = calculate_scheduled_pmt(balance, wac / 12, term)
    assert np.isclose(total_cf, pmt * term, atol=0.01)


def test_average_life():
    total_principal = np.array([50000, 50000])
    balance = 100000
    al = average_life(total_principal, balance)
    assert np.isclose(al, 0.125)
