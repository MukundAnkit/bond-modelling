import datetime  # noqa: D100
import logging
from typing import ClassVar

import pandas as pd
import pandas_datareader.data as web

from .base import DataFetcher
from .exceptions import DataFetchError, DataNormalizationError

logger = logging.getLogger(__name__)


class SofrFetcher(DataFetcher):
    """Fetches the Secured Overnight Financing Rate (SOFR) and its averages
    to construct a short-term risk-free yield curve.
    """  # noqa: D205

    # Map maturities (in years) to FRED series IDs
    SERIES_MAP: ClassVar[dict[float, str]] = {
        1 / 365: "SOFR",  # Overnight
        30 / 365: "SOFR30DAYAVG",  # 30-day average
        90 / 365: "SOFR90DAYAVG",  # 90-day average
        180 / 365: "SOFR180DAYAVG",  # 180-day average
    }

    def fetch_yield_curve(self, date: datetime.date) -> dict[float, float]:
        """Fetches the SOFR curve for the given date.

        Args:
            date (datetime.date): The date for which to fetch the curve.

        Returns:
            Dict[float, float]: Dictionary mapping maturity (in years) to decimal yield.

        """  # noqa: D401, W293
        logger.info(f"Fetching SOFR curve from FRED for date {date}")

        start_date = date - datetime.timedelta(days=7)
        end_date = date
        curve = {}

        try:
            # Fetch all series at once for efficiency
            df = web.DataReader(
                list(self.SERIES_MAP.values()), "fred", start_date, end_date
            )
        except Exception as e:
            logger.error(f"Failed to fetch SOFR data from FRED: {e}")
            raise DataFetchError(f"FRED SOFR API fetch failed: {e}") from e

        if df.empty:
            raise DataFetchError(f"No SOFR data returned from FRED up to {date}")

        try:
            # Forward fill missing values
            df = df.ffill()
            latest_row = df.iloc[-1]

            for maturity, series_id in self.SERIES_MAP.items():
                val = latest_row.get(series_id)
                if pd.isna(val):
                    logger.warning(f"SOFR series {series_id} is NaN around {date}")
                    continue

                # FRED SOFR yields are in percentage points (e.g., 5.05 for 5.05%)
                curve[maturity] = float(val) / 100.0

            if not curve:
                raise DataFetchError(f"All SOFR series were NaN around {date}")

            return dict(sorted(curve.items()))

        except Exception as e:
            if isinstance(e, DataFetchError):
                raise
            raise DataNormalizationError(f"Error normalizing SOFR data: {e}") from e
