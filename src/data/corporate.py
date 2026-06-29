import logging
import datetime
from typing import Dict, ClassVar

import pandas as pd
import pandas_datareader.data as web
from requests.exceptions import RequestException

from .base import DataFetcher
from .exceptions import DataFetchError, DataNormalizationError

logger = logging.getLogger(__name__)

class CorporateFetcher(DataFetcher):
    """
    Fetches ICE BofA US Corporate Index Effective Yields from FRED.
    These are aggregate indices rather than a specific maturity curve.
    """
    
    # Map ratings to FRED series IDs
    SERIES_MAP: ClassVar[Dict[str, str]] = {
        'ALL': 'BAMLC0A0CMEY',       # Broad US Corporate
        'AAA': 'BAMLC0A1CAEY',       # AAA US Corporate
        'AA': 'BAMLC0A2CAAEY',       # AA US Corporate
        'A': 'BAMLC0A3CAEY',         # A US Corporate
        'BBB': 'BAMLC0A4CBBBEY',     # BBB US Corporate
        'HY': 'BAMLH0A0HYM2EY',      # High Yield
    }

    def __init__(self, rating: str = 'ALL', proxy_maturity: float = 7.0):
        """
        Initialize the corporate fetcher.
        
        Args:
            rating (str): The credit rating bucket to fetch (e.g., 'AAA', 'BBB').
            proxy_maturity (float): The maturity to map this index yield to in the curve dictionary, 
                                    since index yields don't have a single defined maturity.
                                    Default is 7.0 (approximate average duration of corporate index).
        """
        self.rating = rating.upper()
        if self.rating not in self.SERIES_MAP:
            raise ValueError(f"Rating {self.rating} not supported. Use one of {list(self.SERIES_MAP.keys())}")
        
        self.series_id = self.SERIES_MAP[self.rating]
        self.proxy_maturity = proxy_maturity

    def fetch_yield_curve(self, date: datetime.date) -> Dict[float, float]:
        """
        Fetches the index yield for the given date and returns it mapped to the proxy maturity.
        
        Returns:
            Dict[float, float]: e.g. {7.0: 0.0521}
        """
        logger.info(f"Fetching Corporate {self.rating} index yield from FRED for date {date}")
        
        # Lookback window to handle weekends/holidays (e.g. forward fill from Friday)
        start_date = date - datetime.timedelta(days=7)
        end_date = date
        
        try:
            df = web.DataReader(
                self.series_id,
                'fred',
                start_date,
                end_date
            )
        except Exception as e:
            logger.error(f"Failed to fetch {self.series_id} from FRED: {e}")
            raise DataFetchError(f"FRED corporate API fetch failed: {e}") from e

        if df.empty:
            raise DataFetchError(f"No corporate data returned from FRED for {self.series_id} up to {date}")

        try:
            # Forward fill missing values
            df = df.ffill()
            
            # Extract the yield for the requested date (or the most recent available date prior to it)
            # The index is datetime, we ensure it's up to end_date
            latest_yield = df.iloc[-1][self.series_id]
            
            if pd.isna(latest_yield):
                raise DataFetchError(f"Corporate yield data is NaN for {self.series_id} around {date}")
                
            # FRED corporate yields are in percentage points (e.g., 5.21 for 5.21%)
            # We normalize to decimal
            decimal_yield = float(latest_yield) / 100.0
            
            return {self.proxy_maturity: decimal_yield}
            
        except Exception as e:
            if isinstance(e, DataFetchError):
                raise
            raise DataNormalizationError(f"Error normalizing Corporate yield data: {e}") from e
