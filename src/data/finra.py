import datetime
import logging
from typing import Dict

from .base import DataFetcher

logger = logging.getLogger(__name__)


class MockFinraFetcher(DataFetcher):
    """
    Simulates FINRA market data for corporate and municipal bonds.
    Due to strict FINRA scraping policies, this mock uses a base Treasury curve 
    and applies realistic spreads.
    """
    
    def __init__(self, base_curve: Dict[float, float], spread_bps: float = 50.0, is_municipal: bool = False):
        """
        Args:
            base_curve: The reference Treasury yield curve (decimal format).
            spread_bps: The credit spread to add to the base yield (in basis points).
            is_municipal: If true, applies a tax-exempt ratio (e.g. 0.78) to the base yield before adding spread.
        """
        self.base_curve = base_curve
        self.spread_decimal = spread_bps / 10000.0
        self.tax_exempt_ratio = 0.78 if is_municipal else 1.0
        self.is_municipal = is_municipal

    def fetch_yield_curve(self, date: datetime.date) -> Dict[float, float]:
        """
        Generate mock yields. The `date` parameter is ignored since the base curve
        is provided during initialization for the sake of the mock.
        """
        logger.debug(f"Generating Mock FINRA data (Municipal: {self.is_municipal}, Spread: {self.spread_decimal*10000:.1f} bps)")
        
        curve = {}
        for maturity, base_yield in self.base_curve.items():
            # Adjust base yield for tax exemption if municipal, then add spread
            adjusted_yield = (base_yield * self.tax_exempt_ratio) + self.spread_decimal
            curve[maturity] = adjusted_yield
            
        return curve
