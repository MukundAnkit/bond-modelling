"""Yield curve data validation and alignment helper functions."""

from typing import Any


def _to_decimal_yield(val: float) -> float:
    """Standardize raw yield inputs to decimal representation.

    Detects the scale automatically:
    - If absolute value is > 10.0: assumed to be CBOE 10x scale (e.g. 43.50 -> 0.0435).
    - If absolute value is > 0.2: assumed to be percentage scale (e.g. 4.35 -> 0.0435).
    - Otherwise: assumed to be already in decimal form (e.g. 0.0435).

    """
    if abs(val) > 10.0:
        return float(val) / 1000.0
    elif abs(val) > 0.2:
        return float(val) / 100.0
    return float(val)


def cross_validate_yields(
    source_a: dict[str, float],
    source_b: dict[str, float],
    max_diff_bps: float = 5.0,
) -> list[dict[str, Any]]:
    """Compare yields of identical maturities from two different data sources.

    Standardizes inputs to decimal format automatically, computes the absolute
    difference in basis points (bps), and flags discrepancies exceeding
    the tolerance limit.

    Parameters
    ----------
    source_a : dict of (str, float)
        Maturity keys mapped to yield values from Source A (e.g., FRED).
    source_b : dict of (str, float)
        Maturity keys mapped to yield values from Source B (e.g., yfinance).
    max_diff_bps : float, optional
        Maximum allowable difference in basis points. Default is ``5.0``.

    Returns
    -------
    list of dict
        A list of discrepancy details for any maturities exceeding the tolerance.

    """
    discrepancies = []
    common_keys = set(source_a.keys()).intersection(source_b.keys())

    for key in sorted(common_keys):
        y_a = _to_decimal_yield(source_a[key])
        y_b = _to_decimal_yield(source_b[key])

        diff_bps = abs(y_a - y_b) * 10000.0
        if diff_bps > max_diff_bps:
            discrepancies.append(
                {
                    "maturity": key,
                    "val_a": y_a,
                    "val_b": y_b,
                    "diff_bps": diff_bps,
                }
            )

    return discrepancies
