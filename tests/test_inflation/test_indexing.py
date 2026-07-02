import pytest

from src.inflation.indexing import daily_ref_cpi, index_ratio


def test_daily_ref_cpi():
    cpi_m3 = 250.0
    cpi_m2 = 253.0
    # Day 1 should be exactly cpi_m3
    assert daily_ref_cpi(cpi_m3, cpi_m2, 1, 30) == 250.0
    # Day 16 of a 30-day month -> ratio = 15 / 30 = 0.5 -> 251.5
    assert daily_ref_cpi(cpi_m3, cpi_m2, 16, 30) == 251.5
    # Day 30 of a 30-day month -> ratio = 29 / 30 -> 252.9
    assert (
        pytest.approx(daily_ref_cpi(cpi_m3, cpi_m2, 30, 30)) == 250.0 + (29 / 30) * 3.0
    )


def test_daily_ref_cpi_invalid():
    with pytest.raises(ValueError):
        daily_ref_cpi(250.0, 253.0, 1, 0)
    with pytest.raises(ValueError):
        daily_ref_cpi(250.0, 253.0, 32, 31)


def test_index_ratio():
    assert index_ratio(260.0, 250.0) == 1.04
    with pytest.raises(ValueError):
        index_ratio(260.0, 0.0)
