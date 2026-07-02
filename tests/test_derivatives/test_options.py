"""Unit tests for Caps, Floors, and Swaptions.
"""
import numpy as np
import pytest

from src.derivatives.cap_floor import Cap, Floor, cap_floor_pv
from src.derivatives.swap import InterestRateSwap, swap_pv
from src.derivatives.swaption import Swaption, price_swaption_jamshidian
from src.models.stochastic import VasicekModel


def test_cap_floor_parity():
    # Vasicek model parameters
    a = 0.1
    b = 0.05
    sigma = 0.01
    model = VasicekModel(a, b, sigma)

    r_t = 0.05
    notional = 1e6
    strike = 0.05
    tenor = 5.0
    freq = 2

    # Cap and Floor
    cap = Cap(notional, strike, tenor, freq)
    floor = Floor(notional, strike, tenor, freq)

    # Prices
    pv_cap = cap_floor_pv(cap, model, r_t)
    pv_floor = cap_floor_pv(floor, model, r_t)

    # Payer swap with fixed rate = strike
    # curve is given by model's zcb_price. We need a wrapper to give continuous rate y(t)
    def curve(t):
        if t == 0:
            return r_t
        zcb = model.zcb_price(r_t, t)
        return -float(np.log(zcb)) / t

    swap = InterestRateSwap(notional, strike, tenor, freq)
    pv_swap = swap_pv(swap, curve, position="payer")

    # Cap - Floor = Payer Swap
    assert (pv_cap - pv_floor) == pytest.approx(pv_swap, rel=1e-3, abs=1e-2)


def test_swaption_parity():
    # Vasicek model parameters
    a = 0.1
    b = 0.05
    sigma = 0.01
    model = VasicekModel(a, b, sigma)

    r_t = 0.05
    notional = 1e6
    strike = 0.05

    # 5-year swap starting in 2 years
    expiry = 2.0
    swap_tenor = 7.0  # absolute maturity
    freq = 2

    swap = InterestRateSwap(notional, strike, swap_tenor, freq)

    payer_swaption = Swaption(swap, expiry, "payer")
    receiver_swaption = Swaption(swap, expiry, "receiver")

    pv_payer_swaption = price_swaption_jamshidian(payer_swaption, model, r_t)
    pv_receiver_swaption = price_swaption_jamshidian(receiver_swaption, model, r_t)

    # PV of forward starting payer swap
    # PV_forward_swap = PV_swap(t=0) - PV_swap_payments_before_expiry
    # But since swap_pv calculates from t=0 to tenor, we need to subtract the payments up to expiry.
    def curve(t):
        if t == 0:
            return r_t
        zcb = model.zcb_price(r_t, t)
        return -float(np.log(zcb)) / t

    pv_payer_full = swap_pv(swap, curve, position="payer")

    # Payer swap up to expiry
    short_swap = InterestRateSwap(notional, strike, expiry, freq)
    pv_payer_short = swap_pv(short_swap, curve, position="payer")

    pv_forward_swap = pv_payer_full - pv_payer_short

    assert (pv_payer_swaption - pv_receiver_swaption) == pytest.approx(pv_forward_swap, rel=1e-3, abs=1e-2)  # noqa: E501
