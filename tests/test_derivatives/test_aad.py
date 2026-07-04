"""Unit tests for AAD framework."""

import pytest

from src.derivatives.aad import Dual
from src.derivatives.bachelier import bachelier_formula


def test_dual_number_basic():
    x = Dual(2.0)
    y = Dual(3.0)

    # z = x * y + x^2
    z = x * y + x**2

    assert float(z) == 10.0
    z.backward()

    # dz/dx = y + 2x = 3 + 4 = 7
    # dz/dy = x = 2
    assert x.adjoint == 7.0
    assert y.adjoint == 2.0


def test_bachelier_aad_greeks():
    fwd = Dual(0.05)
    strike = Dual(0.05)
    t_exp = Dual(2.0)
    vol = Dual(0.0050)
    df = Dual(0.90)

    px = bachelier_formula(fwd, strike, t_exp, vol, df, is_call=True)
    px.backward()

    delta = fwd.adjoint
    vega = vol.adjoint

    # Calculate finite difference for verification
    bump = 1e-6
    px_up = bachelier_formula(0.05 + bump, 0.05, 2.0, 0.0050, 0.90, True)
    px_dn = bachelier_formula(0.05 - bump, 0.05, 2.0, 0.0050, 0.90, True)
    fd_delta = (px_up - px_dn) / (2 * bump)

    assert delta == pytest.approx(fd_delta, rel=1e-4)

    px_up_v = bachelier_formula(0.05, 0.05, 2.0, 0.0050 + bump, 0.90, True)
    px_dn_v = bachelier_formula(0.05, 0.05, 2.0, 0.0050 - bump, 0.90, True)
    fd_vega = (px_up_v - px_dn_v) / (2 * bump)

    assert vega == pytest.approx(fd_vega, rel=1e-4)
