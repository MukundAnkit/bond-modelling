"""Tests for accrued interest and dirty/clean price functions."""

from datetime import date

import pytest

from src.instruments.day_count import year_fraction
from src.instruments.pricing import (
    accrued_interest,
    clean_price_from_dirty,
    dirty_price,
)


class TestAccruedInterest:
    def test_zero_fraction(self) -> None:
        assert accrued_interest(25.0, 0.0) == 0.0

    def test_half_period(self) -> None:
        assert accrued_interest(25.0, 0.5) == pytest.approx(12.5)

    def test_full_period(self) -> None:
        assert accrued_interest(25.0, 1.0) == pytest.approx(25.0)

    def test_practical_example(self) -> None:
        coupon = 1000 * 0.05 / 2  # 25.0 semi-annual coupon
        settlement = date(2025, 4, 15)
        last_coupon = date(2025, 1, 15)
        next_coupon = date(2025, 7, 15)
        frac = year_fraction(last_coupon, settlement, "act_act") / year_fraction(
            last_coupon, next_coupon, "act_act"
        )
        ai = accrued_interest(coupon, frac)
        assert 0 < ai < coupon


class TestDirtyPrice:
    def test_dirty_from_clean(self) -> None:
        assert dirty_price(100.0, 2.5) == 102.5

    def test_clean_from_dirty(self) -> None:
        assert clean_price_from_dirty(102.5, 2.5) == 100.0

    def test_round_trip(self) -> None:
        clean = 98.75
        ai = 1.25
        assert clean_price_from_dirty(dirty_price(clean, ai), ai) == pytest.approx(
            clean
        )

    def test_zero_accrued(self) -> None:
        assert dirty_price(100.0, 0.0) == 100.0
        assert clean_price_from_dirty(100.0, 0.0) == 100.0
