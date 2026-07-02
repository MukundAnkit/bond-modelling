# ruff: noqa
import numpy as np
from src.exotics.tarn import TargetRedemptionNote


def test_tarn_pricing():
    notional = 100000
    target_cap = 0.10  # 10% total coupons

    def coupon_func(p, t):
        return 0.03  # constant 3%

    def funding_func(p, t):
        return 0.02  # constant 2% discount rate

    tarn = TargetRedemptionNote(notional, target_cap, coupon_func, funding_func)

    payment_times = [1.0, 2.0, 3.0, 4.0, 5.0]

    price, stderr = tarn.price(n_paths=10, payment_times=payment_times, dt=1.0)

    assert price > 0
    assert stderr == 0.0  # Deterministic paths
