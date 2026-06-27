import numpy as np

from src.module1_pricing.bond import Bond


def price(bond: Bond, yield_rate: float) -> float:
    rate_per_period = yield_rate / bond.freq
    t = np.arange(1, bond.periods + 1)
    pv_coupons = np.sum(bond.coupon_payment / (1 + rate_per_period) ** t)
    pv_face = bond.face_value / (1 + rate_per_period) ** bond.periods
    return float(pv_coupons + pv_face)
