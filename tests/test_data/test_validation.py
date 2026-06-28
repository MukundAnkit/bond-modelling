"""Tests for yield curve data cross-validation and scaling checks."""

import pytest

from src.data.validation import cross_validate_yields


def test_cross_validate_within_tolerance() -> None:
    """Test validation when yields match within basis point tolerance."""
    # Source A: FRED format (yields in percent, e.g. 4.25 for 4.25% -> 0.0425)
    # Source B: yfinance format (CBOE options scale, e.g. 42.60 for 4.26% -> 0.0426)
    source_a = {"10Y": 4.25}  # 4.25%
    source_b = {"10Y": 42.60}  # 4.26% (10 bps diff)

    # 10 bps is 10 basis points difference. If tolerance is 15 bps, it passes.
    discrepancies = cross_validate_yields(source_a, source_b, max_diff_bps=15.0)
    assert len(discrepancies) == 0


def test_cross_validate_outside_tolerance() -> None:
    """Test validation when yields differ by more than the tolerance limit."""
    source_a = {"10Y": 4.25}  # 4.25%
    source_b = {"10Y": 43.50}  # 4.35% (10 bps difference)

    discrepancies = cross_validate_yields(source_a, source_b, max_diff_bps=5.0)
    assert len(discrepancies) == 1
    assert discrepancies[0]["maturity"] == "10Y"
    assert discrepancies[0]["diff_bps"] == pytest.approx(10.0, abs=1e-12)


def test_cross_validate_missing_keys() -> None:
    """Test validation when maturities are mismatched between sources."""
    source_a = {"5Y": 4.0, "10Y": 4.25}
    source_b = {"10Y": 42.5}  # Missing 5Y

    discrepancies = cross_validate_yields(source_a, source_b, max_diff_bps=5.0)
    # Should not crash, just validate the keys that are present in both
    assert len(discrepancies) == 0
