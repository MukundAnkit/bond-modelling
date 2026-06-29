import datetime  # noqa: D100
import logging
from typing import ClassVar

import pandas as pd
import pandas_datareader.data as web

from .base import DataFetcher
from .exceptions import DataFetchError, DataNormalizationError

logger = logging.getLogger(__name__)


class GlobalSovereignFetcher(DataFetcher):
    """Fetches Long-Term (10-Year) Government Bond Yields for global sovereigns from FRED.
    These are monthly series (Long-Term Interest Rates) published by the OECD, so we
    forward-fill to approximate daily pricing.
    """  # noqa: D205, E501, W291

    # Map regions to FRED series IDs (Long-Term Interest Rates, % per annum)
    SERIES_MAP: ClassVar[dict[str, str]] = {
        "EUR": "IRLTLT01EZM156N",  # Euro Area (19 countries)
        "DEU": "IRLTLT01DEM156N",  # Germany
        "GBR": "IRLTLT01GBM156N",  # United Kingdom
        "JPN": "IRLTLT01JPM156N",  # Japan
    }

    def __init__(self, region: str = "EUR"):
        """Initialize the global sovereign fetcher.

        Args:
            region (str): The region code (e.g., 'EUR', 'DEU', 'GBR', 'JPN').

        """  # noqa: W293
        self.region = region.upper()
        if self.region not in self.SERIES_MAP:
            raise ValueError(
                f"Region {self.region} not supported. Use one of {list(self.SERIES_MAP.keys())}"
            )  # noqa: E501

        self.series_id = self.SERIES_MAP[self.region]

    def fetch_yield_curve(self, date: datetime.date) -> dict[float, float]:
        """Fetches the 10-year yield for the given date.

        Returns:
            Dict[float, float]: Dictionary mapping 10.0 (years) to decimal yield.

        """  # noqa: D401, W293
        logger.info(
            f"Fetching 10-year Sovereign Yield for {self.region} from FRED for date {date}"
        )  # noqa: E501

        # Monthly data requires a wider lookback window (e.g. 60 days) to find the most recent month  # noqa: E501
        start_date = date - datetime.timedelta(days=60)
        end_date = date

        try:
            df = web.DataReader(self.series_id, "fred", start_date, end_date)
        except Exception as e:
            logger.error(f"Failed to fetch {self.series_id} from FRED: {e}")
            raise DataFetchError(f"FRED Global Sovereign API fetch failed: {e}") from e

        if df.empty:
            raise DataFetchError(
                f"No sovereign data returned from FRED for {self.series_id} up to {date}"
            )  # noqa: E501

        try:
            # Forward fill the monthly values to approximate the requested daily date
            df = df.ffill()
            latest_yield = df.iloc[-1][self.series_id]

            if pd.isna(latest_yield):
                raise DataFetchError(
                    f"Sovereign yield data is NaN for {self.series_id} around {date}"
                )  # noqa: E501

            # OECD yields are in percentage points (e.g., 2.50 for 2.50%)
            decimal_yield = float(latest_yield) / 100.0

            # The OECD series represents the 10-Year government bond
            return {10.0: decimal_yield}

        except Exception as e:
            if isinstance(e, DataFetchError):
                raise
            raise DataNormalizationError(
                f"Error normalizing Global Sovereign data: {e}"
            ) from e  # noqa: E501
