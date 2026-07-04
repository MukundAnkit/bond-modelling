"""Tests for day count conventions."""

from datetime import date

import pytest

from src.instruments.day_count import (
    act_360,
    act_365,
    act_act,
    thirty_360,
    year_fraction,
)


class TestThirty360:
    def test_same_date(self) -> None:
        assert thirty_360(date(2025, 1, 1), date(2025, 1, 1)) == 0.0

    def test_one_month(self) -> None:
        frac = thirty_360(date(2025, 1, 1), date(2025, 2, 1))
        assert frac == pytest.approx(1.0 / 12.0)

    def test_one_year(self) -> None:
        frac = thirty_360(date(2025, 1, 15), date(2026, 1, 15))
        assert frac == pytest.approx(1.0)

    def test_31st_adjustment(self) -> None:
        frac = thirty_360(date(2025, 1, 31), date(2025, 2, 28))
        assert frac == pytest.approx(28.0 / 360.0)

    def test_end_date_31st_with_start_30th(self) -> None:
        frac = thirty_360(date(2025, 4, 30), date(2025, 5, 31))
        # Both start (30th) and end (31st) are adjusted to day 30 under US rule
        assert frac == pytest.approx(30.0 / 360.0)


class TestActAct:
    def test_same_date(self) -> None:
        assert act_act(date(2025, 1, 1), date(2025, 1, 1)) == 0.0

    def test_one_day(self) -> None:
        frac = act_act(date(2025, 1, 1), date(2025, 1, 2))
        assert frac == pytest.approx(1.0 / 365.0)

    def test_one_year_non_leap(self) -> None:
        frac = act_act(date(2025, 1, 1), date(2026, 1, 1))
        assert frac == pytest.approx(1.0, abs=1e-10)

    def test_crosses_leap_year(self) -> None:
        frac = act_act(date(2023, 7, 1), date(2024, 7, 1))
        # Act/Act ISMA splits across calendar years; a leap-year span can
        # produce a fraction > 1.0
        days_2023 = (date(2023, 12, 31) - date(2023, 7, 1)).days + 1
        days_2024 = (date(2024, 7, 1) - date(2024, 1, 1)).days
        expected = days_2023 / 365.0 + days_2024 / 366.0
        assert frac == pytest.approx(expected, abs=1e-10)

    def test_feb_29_included(self) -> None:
        frac = act_act(date(2024, 2, 28), date(2024, 2, 29))
        assert frac == pytest.approx(1.0 / 366.0)


class TestAct360:
    def test_one_year(self) -> None:
        frac = act_360(date(2025, 1, 1), date(2026, 1, 1))
        assert frac == pytest.approx(365.0 / 360.0)

    def test_six_months(self) -> None:
        frac = act_360(date(2025, 1, 1), date(2025, 7, 1))
        assert frac == pytest.approx(181.0 / 360.0)


class TestAct365:
    def test_one_year(self) -> None:
        frac = act_365(date(2025, 1, 1), date(2026, 1, 1))
        assert frac == pytest.approx(1.0)

    def test_leap_year(self) -> None:
        frac = act_365(date(2024, 1, 1), date(2025, 1, 1))
        assert frac == pytest.approx(366.0 / 365.0)


class TestYearFraction:
    def test_unknown_convention(self) -> None:
        with pytest.raises(ValueError, match="Unknown day count convention"):
            year_fraction(date(2025, 1, 1), date(2025, 2, 1), convention="unknown")

    def test_delegates_correctly(self) -> None:
        d1 = date(2025, 1, 1)
        d2 = date(2025, 7, 1)
        assert year_fraction(d1, d2, "30/360") == thirty_360(d1, d2)
        assert year_fraction(d1, d2, "act_act") == act_act(d1, d2)
        assert year_fraction(d1, d2, "act_360") == act_360(d1, d2)
        assert year_fraction(d1, d2, "act_365") == act_365(d1, d2)
