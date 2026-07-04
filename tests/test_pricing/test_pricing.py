import pytest

from src.instruments.bond import Bond
from src.instruments.pricing import price


def test_bond_creation():
    b = Bond(face_value=1000, coupon_rate=0.05, maturity=3.0, freq=2)
    assert b.periods == 6
    assert b.coupon_payment == 25.0


def test_bond_invalid_face_value():
    with pytest.raises(ValueError):
        Bond(face_value=-100, coupon_rate=0.05, maturity=3.0)


def test_bond_invalid_coupon():
    with pytest.raises(ValueError):
        Bond(face_value=1000, coupon_rate=-0.01, maturity=3.0)


def test_bond_invalid_maturity():
    with pytest.raises(ValueError):
        Bond(face_value=1000, coupon_rate=0.05, maturity=0)


def test_bond_invalid_freq():
    with pytest.raises(ValueError):
        Bond(face_value=1000, coupon_rate=0.05, maturity=3.0, freq=3)


def test_price_par_bond():
    b = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
    p = price(b, 0.05)
    assert p == pytest.approx(100.0, abs=1e-2)


def test_price_premium_bond():
    b = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
    p = price(b, 0.04)
    assert p == pytest.approx(102.80, abs=1e-2)


def test_price_discount_bond():
    b = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
    p = price(b, 0.06)
    assert p == pytest.approx(97.29, abs=1e-2)


def test_price_zero_coupon():
    b = Bond(face_value=100, coupon_rate=0.0, maturity=5.0, freq=1)
    p = price(b, 0.03)
    expected = 100 / (1.03**5)
    assert p == pytest.approx(expected, abs=1e-6)


def test_zero_coupon_price_annual():
    from src.instruments.pricing import zero_coupon_price

    p = zero_coupon_price(100, 0.03, 5.0, compounding_freq=1)
    expected = 100 / (1.03**5)
    assert p == pytest.approx(expected, abs=1e-10)


def test_zero_coupon_price_semi_annual():
    from src.instruments.pricing import zero_coupon_price

    p = zero_coupon_price(100, 0.03, 5.0, compounding_freq=2)
    expected = 100 / (1.015**10)
    assert p == pytest.approx(expected, abs=1e-10)


def test_zero_coupon_price_default_freq():
    from src.instruments.pricing import zero_coupon_price

    p = zero_coupon_price(100, 0.03, 5.0)
    expected = 100 / (1.015**10)
    assert p == pytest.approx(expected, abs=1e-10)


def test_zero_coupon_price_quarterly():
    from src.instruments.pricing import zero_coupon_price

    p = zero_coupon_price(100, 0.04, 3.0, compounding_freq=4)
    expected = 100 / (1.01**12)
    assert p == pytest.approx(expected, abs=1e-10)


def test_zero_coupon_price_zero_yield():
    from src.instruments.pricing import zero_coupon_price

    p = zero_coupon_price(100, 0.0, 5.0)
    assert p == pytest.approx(100.0, abs=1e-10)
