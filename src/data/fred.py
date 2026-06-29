import datetime
import logging
from typing import Dict

import pandas as pd
import pandas_datareader.data as web
from requests.exceptions import RequestException

from .base import DataFetcher
from .exceptions import DataFetchError, DataNormalizationError, MarketHolidayError

logger = logging.getLogger(__name__)


class FredFetcher(DataFetcher):
    """Fetches constant maturity Treasury yields from FRED."""
    
    SERIES_MAPPING = {
        "DGS3MO": 0.25,
        "DGS1": 1.0,
        "DGS2": 2.0,
        "DGS5": 5.0,
        "DGS10": 10.0,
        "DGS30": 30.0,
    }

    def fetch_yield_curve(self, date: datetime.date) -> Dict[float, float]:
        """
        Fetch FRED Treasury yields for a specific date.
        Uses forward fill to handle weekends and holidays.
        """
        series_ids = list(self.SERIES_MAPPING.keys())
        # To support forward filling for holidays, we fetch a 10-day window ending on the requested date.
        start_date = date - datetime.timedelta(days=10)
        
        try:
            df = web.DataReader(series_ids, "fred", start_date, date)
        except (RequestException, IOError) as e:
            logger.error(f"Failed to fetch from FRED: {e}")
            raise DataFetchError(f"FRED fetch failed: {e}") from e
            
        if df.empty:
            raise MarketHolidayError(f"No FRED data available for {date} (or preceding days).")
            
        # Forward fill to handle NaNs (e.g., if a specific series is missing on a day where others are present)
        df = df.ffill()
        
        # Get the row corresponding to the requested date (or the most recent available date if requested is holiday)
        # Using the last row since we fetched up to the requested date.
        try:
            latest_row = df.iloc[-1]
            actual_date = latest_row.name.date()
        except IndexError:
            raise DataNormalizationError("FRED returned empty dataframe after parsing.")
            
        if actual_date > date:
             # Should not happen as we bound the end date, but good to check.
             raise MarketHolidayError(f"Available date {actual_date} is past requested date {date}.")

        logger.debug(f"FRED raw response for {actual_date}: {latest_row.to_dict()}")

        curve = {}
        for series_id, maturity in self.SERIES_MAPPING.items():
            val = latest_row.get(series_id)
            if pd.isna(val):
                continue
            # FRED yields are percentages (e.g., 4.25), convert to decimal
            try:
                curve[maturity] = float(val) / 100.0
            except ValueError as e:
                raise DataNormalizationError(f"Could not convert FRED value {val} to float") from e

        if not curve:
            raise DataNormalizationError("No valid yields found in FRED response.")
            
        return curve
