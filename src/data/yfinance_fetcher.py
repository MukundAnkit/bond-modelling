import datetime
import logging
from typing import Dict

import pandas as pd
import yfinance as yf

from .base import DataFetcher
from .exceptions import DataFetchError, DataNormalizationError, MarketHolidayError

logger = logging.getLogger(__name__)


class YFinanceFetcher(DataFetcher):
    """Fetches benchmark Treasury yields from Yahoo Finance."""
    
    TICKER_MAPPING = {
        "^IRX": 0.25,
        "^FVX": 5.0,
        "^TNX": 10.0,
        "^TYX": 30.0,
    }

    def fetch_yield_curve(self, date: datetime.date) -> Dict[float, float]:
        """
        Fetch Yahoo Finance Treasury yields for a specific date.
        """
        tickers = list(self.TICKER_MAPPING.keys())
        
        # yfinance download expects strings, and to get a specific date, we fetch a short window
        start_date_str = (date - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        # To include the requested date, we need to ask up to the day after
        end_date_str = (date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        try:
            # Multi-ticker download returns a dataframe with multi-level columns if multiple tickers
            df = yf.download(tickers, start=start_date_str, end=end_date_str, progress=False)
        except Exception as e:
            logger.error(f"Failed to fetch from YFinance: {e}")
            raise DataFetchError(f"YFinance fetch failed: {e}") from e
            
        if df.empty:
            raise MarketHolidayError(f"No YFinance data available for {date}.")
            
        # We only care about the "Close" prices
        if "Close" in df.columns:
            close_df = df["Close"]
        else:
            raise DataNormalizationError("YFinance response missing 'Close' column.")
            
        # Forward fill missing values
        close_df = close_df.ffill()
        
        # Filter for dates up to the requested date
        mask = close_df.index.date <= date
        filtered_df = close_df[mask]
        
        if filtered_df.empty:
            raise MarketHolidayError(f"No YFinance data available up to {date}.")
            
        latest_row = filtered_df.iloc[-1]
        actual_date = latest_row.name.date()
        
        logger.debug(f"YFinance raw response for {actual_date}: {latest_row.to_dict()}")
        
        curve = {}
        for ticker, maturity in self.TICKER_MAPPING.items():
            val = latest_row.get(ticker)
            if pd.isna(val):
                continue
            # YFinance treasury yields are 10x the percentage yield (e.g., 42.5 for 4.25%)
            # Convert to decimal by dividing by 1000
            try:
                curve[maturity] = float(val) / 1000.0
            except ValueError as e:
                raise DataNormalizationError(f"Could not convert YFinance value {val} to float") from e

        if not curve:
            raise DataNormalizationError("No valid yields found in YFinance response.")
            
        return curve
