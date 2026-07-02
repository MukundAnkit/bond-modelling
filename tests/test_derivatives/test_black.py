"""Unit tests for Black's model pricing."""
import numpy as np
import pytest

from src.derivatives.black import black_formula
from src.derivatives.cap_floor import Cap, Floor, cap_floor_black
from src.derivatives.swap import InterestRateSwap, swap_pv
from src.derivatives.swaption import Swaption, price_swaption_black

def test_black_formula():
    # ATM option
    F = 0.05
    K = 0.05
    T = 2.0
    sigma = 0.20
    df = 0.90
    
    call_px = black_formula(F, K, T, sigma, df, is_call=True)
    put_px = black_formula(F, K, T, sigma, df, is_call=False)
    
    # Put-Call Parity: Call - Put = df * (F - K)
    assert (call_px - put_px) == pytest.approx(df * (F - K), abs=1e-6)
    assert call_px > 0
    assert put_px > 0

def test_black_cap_floor_parity():
    # Parity: Cap - Floor = Payer Swap
    notional = 1e6
    strike = 0.04
    tenor = 5.0
    freq = 2
    
    cap = Cap(notional, strike, tenor, freq)
    floor = Floor(notional, strike, tenor, freq)
    
    def curve(t):
        return 0.04  # Flat continuous yield
        
    vol = 0.20
    pv_cap = cap_floor_black(cap, curve, vol)
    pv_floor = cap_floor_black(floor, curve, vol)
    
    # Underlying swap
    swap = InterestRateSwap(notional, strike, tenor, freq)
    pv_swap = swap_pv(swap, curve, position="payer")
    
    # We must match Cap - Floor = Swap
    # Actually, caplet and floorlet are on forward LIBOR, while swap is on fixed vs float.
    # Standard Cap-Floor parity: Cap - Floor = Payer Swap (if they have the same schedule, and first period is also included).
    assert (pv_cap - pv_floor) == pytest.approx(pv_swap, rel=1e-3, abs=1e-2)

def test_black_swaption_parity():
    notional = 1e6
    strike = 0.04
    swap_tenor = 7.0
    expiry = 2.0
    freq = 2
    
    swap = InterestRateSwap(notional, strike, swap_tenor, freq)
    
    payer_swaption = Swaption(swap, expiry, "payer")
    receiver_swaption = Swaption(swap, expiry, "receiver")
    
    def curve(t):
        return 0.04  # Flat continuous yield
        
    vol = 0.20
    
    pv_payer = price_swaption_black(payer_swaption, curve, vol)
    pv_receiver = price_swaption_black(receiver_swaption, curve, vol)
    
    # PV of forward starting payer swap
    pv_payer_full = swap_pv(swap, curve, position="payer")
    short_swap = InterestRateSwap(notional, strike, expiry, freq)
    pv_payer_short = swap_pv(short_swap, curve, position="payer")
    
    pv_forward_swap = pv_payer_full - pv_payer_short
    
    assert (pv_payer - pv_receiver) == pytest.approx(pv_forward_swap, rel=1e-3, abs=1e-2)
