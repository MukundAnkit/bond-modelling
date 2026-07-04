import numpy as np

from mbs.prepayment import (
    cpr_to_smm,
    psa_to_cpr,
    psa_to_smm,
    richard_roll_cpr,
    smm_to_cpr,
)


def test_cpr_to_smm():
    cpr = 0.06
    smm = cpr_to_smm(cpr)
    assert np.isclose(smm, 0.005143, atol=1e-5)

    assert np.isclose(smm_to_cpr(smm), cpr, atol=1e-5)


def test_psa_to_cpr():
    # 100% PSA month 15: 15 * 0.2% = 3%
    assert np.isclose(psa_to_cpr(100, 15), 0.03)
    # 100% PSA month 30: 30 * 0.2% = 6%
    assert np.isclose(psa_to_cpr(100, 30), 0.06)
    # 100% PSA month 40: 6%
    assert np.isclose(psa_to_cpr(100, 40), 0.06)
    # 150% PSA month 15: 15 * 0.2% * 1.5 = 4.5%
    assert np.isclose(psa_to_cpr(150, 15), 0.045)


def test_psa_to_smm():
    cpr = psa_to_cpr(100, 30)  # 0.06
    smm = psa_to_smm(100, 30)
    assert np.isclose(smm, cpr_to_smm(cpr))


def test_richard_roll_cpr():
    cpr1 = richard_roll_cpr(wac=0.06, current_rate=0.04, t=12, month=6, pool_factor=1.0)
    assert 0.0 < cpr1 < 1.0

    cpr2 = richard_roll_cpr(wac=0.04, current_rate=0.06, t=12, month=6, pool_factor=1.0)
    assert cpr2 < cpr1

    cpr3 = richard_roll_cpr(wac=0.06, current_rate=0.04, t=12, month=6, pool_factor=0.5)
    assert cpr3 < cpr1
