"""Module 12: Inflation-Linked Bonds (TIPS)."""

from src.inflation.curves import bootstrap_real_rates, breakeven_inflation
from src.inflation.indexing import daily_ref_cpi, index_ratio
from src.inflation.tips import TIPS

__all__ = [
    "TIPS",
    "bootstrap_real_rates",
    "breakeven_inflation",
    "daily_ref_cpi",
    "index_ratio",
]
