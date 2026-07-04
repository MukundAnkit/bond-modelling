"""Unit tests for SABR and Bachelier models."""

import pytest

from src.derivatives.bachelier import bachelier_formula
from src.derivatives.cap_floor import Cap, Floor, cap_floor_bachelier
from src.derivatives.sabr import sabr_normal_vol
from src.derivatives.swap import InterestRateSwap, swap_pv
from src.derivatives.swaption import Swaption, price_swaption_bachelier


def test_bachelier_formula():
    fwd = 0.05
    strike = 0.05
    t_exp = 2.0
    vol = 0.0050 # 50 bps normal vol
    df = 0.90

    call_px = bachelier_formula(fwd, strike, t_exp, vol, df, is_call=True)
    put_px = bachelier_formula(fwd, strike, t_exp, vol, df, is_call=False)

    # Put-Call Parity: Call - Put = df * (F - K)
    assert float(call_px - put_px) == pytest.approx(df * (fwd - strike), abs=1e-6)
    assert float(call_px) > 0
    assert float(put_px) > 0

def test_sabr_normal_vol():
    fwd = 0.05
    strike = 0.05
    t_exp = 2.0
    alpha = 0.0050
    rho = 0.0
    nu = 0.1

    vol = sabr_normal_vol(fwd, strike, t_exp, alpha, rho, nu)
    assert vol > 0.0

def test_bachelier_cap_floor_parity():
    notional = 1e6
    strike = 0.04
    tenor = 5.0
    freq = 2

    cap = Cap(notional, strike, tenor, freq)
    floor = Floor(notional, strike, tenor, freq)

    def curve(t):
        return 0.04  # Flat continuous yield

    vol = 0.0050
    pv_cap = cap_floor_bachelier(cap, curve, vol=vol)
    pv_floor = cap_floor_bachelier(floor, curve, vol=vol)

    swap = InterestRateSwap(notional, strike, tenor, freq)
    pv_swap = swap_pv(swap, curve, position="payer")

    assert float(pv_cap - pv_floor) == pytest.approx(float(pv_swap), rel=1e-3, abs=1e-2)

def test_bachelier_swaption_parity():
    notional = 1e6
    strike = 0.04
    swap_tenor = 7.0
    expiry = 2.0
    freq = 2

    swap = InterestRateSwap(notional, strike, swap_tenor, freq)
    payer_swaption = Swaption(swap, expiry, "payer")
    receiver_swaption = Swaption(swap, expiry, "receiver")

    def curve(t):
        return 0.04

    vol = 0.0050
    pv_payer = price_swaption_bachelier(payer_swaption, curve, vol=vol)
    pv_receiver = price_swaption_bachelier(receiver_swaption, curve, vol=vol)

    pv_payer_full = swap_pv(swap, curve, position="payer")
    short_swap = InterestRateSwap(notional, strike, expiry, freq)
    pv_payer_short = swap_pv(short_swap, curve, position="payer")

    pv_forward_swap = pv_payer_full - pv_payer_short

    assert float(pv_payer - pv_receiver) == pytest.approx(float(pv_forward_swap), rel=1e-3, abs=1e-2)
