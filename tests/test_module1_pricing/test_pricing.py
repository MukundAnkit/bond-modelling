import pytest
import numpy as np

from src.module1_pricing.bond import Bond
from src.module1_pricing.pricing import price


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
