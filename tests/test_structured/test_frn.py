import numpy as np

from src.structured.frn import FloatingRateNote


def test_frn_pricing_at_par():
    # If the quoted margin equals the discount margin, and reference rate is constant,
    # the FRN should price at par (100).
    frn = FloatingRateNote(
        notional=100.0,
        reference_rate=0.05,
        quoted_margin=0.01,
        payment_frequency=2,
        maturity_years=5.0,
    )
    # Assuming discount_margin = quoted_margin = 0.01
    price = frn.price(discount_margin=0.01)
    np.testing.assert_almost_equal(price, 100.0, decimal=2)


def test_frn_with_margin():
    # If DM > QM, the price should be below par
    frn = FloatingRateNote(
        notional=100.0,
        reference_rate=0.05,
        quoted_margin=0.01,
        payment_frequency=2,
        maturity_years=5.0,
    )
    price = frn.price(discount_margin=0.02)
    assert price < 100.0


def test_frn_negative_rates():
    # Test FRN pricing behavior with negative reference rate and a zero floor
    frn = FloatingRateNote(
        notional=100.0,
        reference_rate=-0.01,
        quoted_margin=0.01,
        payment_frequency=2,
        maturity_years=5.0,
        has_floor=True,
        floor_rate=0.0,
    )
    # The coupon is max(-0.01 + 0.01, 0.0) = 0.0
    price = frn.price(discount_margin=0.0)
    # Without coupons, PV of principal = 100 at DM=0
    np.testing.assert_almost_equal(price, 100.0, decimal=2)
