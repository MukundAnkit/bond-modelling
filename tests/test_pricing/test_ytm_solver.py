import pytest

from src.instruments.bond import Bond
from src.instruments.ytm_solver import ytm_bisection, ytm_newton, ytm_solver


def test_ytm_newton_par():
    b = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
    y = ytm_newton(b, 100.0)
    assert y == pytest.approx(0.05, abs=1e-4)


def test_ytm_newton_premium():
    b = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
    y = ytm_newton(b, 102.80)
    assert y == pytest.approx(0.04, abs=1e-2)


def test_ytm_newton_discount():
    b = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
    y = ytm_newton(b, 97.33)
    assert y == pytest.approx(0.06, abs=1e-2)


def test_ytm_bisection_par():
    b = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
    y = ytm_bisection(b, 100.0)
    assert y == pytest.approx(0.05, abs=1e-4)


def test_ytm_solver_fallback():
    b = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
    y = ytm_solver(b, 100.0)
    assert y == pytest.approx(0.05, abs=1e-4)


def test_ytm_zero_coupon():
    b = Bond(face_value=100, coupon_rate=0.0, maturity=5.0, freq=1)
    y = ytm_solver(b, 100 / (1.03**5))
    assert y == pytest.approx(0.03, abs=1e-4)


def test_ytm_bisection_not_bracketed():
    b = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
    with pytest.raises(ValueError):
        ytm_bisection(b, 200.0, lower=0.0, upper=0.01)


def test_ytm_brentq_par():
    from src.instruments.ytm_solver import ytm_brentq

    b = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
    y = ytm_brentq(b, 100.0)
    assert y == pytest.approx(0.05, abs=1e-4)


def test_ytm_brentq_premium():
    from src.instruments.ytm_solver import ytm_brentq

    b = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
    y = ytm_brentq(b, 102.80)
    assert y == pytest.approx(0.04, abs=1e-2)


def test_ytm_brentq_discount():
    from src.instruments.ytm_solver import ytm_brentq

    b = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
    y = ytm_brentq(b, 97.33)
    assert y == pytest.approx(0.06, abs=1e-2)


def test_ytm_brentq_zero_coupon():
    from src.instruments.ytm_solver import ytm_brentq

    b = Bond(face_value=100, coupon_rate=0.0, maturity=5.0, freq=1)
    y = ytm_brentq(b, 100 / (1.03**5))
    assert y == pytest.approx(0.03, abs=1e-4)


def test_ytm_brentq_not_bracketed():
    from src.instruments.ytm_solver import ytm_brentq

    b = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
    with pytest.raises(ValueError):
        ytm_brentq(b, 200.0, lower=0.0, upper=0.01)


def test_ytm_solver_uses_brentq():
    b = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
    y = ytm_solver(b, 100.0)
    assert y == pytest.approx(0.05, abs=1e-4)
