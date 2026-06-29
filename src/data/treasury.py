import datetime  # noqa: D100
import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base import DataFetcher
from .exceptions import DataFetchError, DataNormalizationError, MarketHolidayError

logger = logging.getLogger(__name__)


class TreasuryFetcher(DataFetcher):
    """Fetches daily Treasury par yield curve rates from the official US Treasury Fiscal Data API."""  # noqa: E501

    BASE_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/daily_treasury_yield_curve"

    FIELD_MAPPING = {
        "bc_1month": 1/12,
        "bc_2month": 2/12,
        "bc_3month": 0.25,
        "bc_4month": 4/12,
        "bc_6month": 0.5,
        "bc_1year": 1.0,
        "bc_2year": 2.0,
        "bc_3year": 3.0,
        "bc_5year": 5.0,
        "bc_7year": 7.0,
        "bc_10year": 10.0,
        "bc_20year": 20.0,
        "bc_30year": 30.0,
    }

    def __init__(self, retries: int = 3, backoff_factor: float = 0.5):  # noqa: D107
        self.session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch_yield_curve(self, date: datetime.date) -> dict[float, float]:
        """Fetch Treasury yields for a specific date.
        """  # noqa: D200
        # The API allows querying exact dates. If a date is a holiday, it returns an empty array.  # noqa: E501
        # To handle holidays similarly to FRED (forward fill), we request a date range.
        start_date = (date - datetime.timedelta(days=10)).strftime("%Y-%m-%d")
        end_date = date.strftime("%Y-%m-%d")

        # Sort by record_date descending to get the most recent date first
        params = {
            "filter": f"record_date:gte:{start_date},record_date:lte:{end_date}",
            "sort": "-record_date",
            "page[size]": "1",
        }

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch from Treasury API: {e}")
            raise DataFetchError(f"Treasury API fetch failed: {e}") from e
        except ValueError as e:
            raise DataNormalizationError(f"Failed to parse Treasury JSON response: {e}") from e  # noqa: E501

        records = data.get("data", [])
        if not records:
            raise MarketHolidayError(f"No Treasury data available up to {date}.")

        latest_record = records[0]
        logger.debug(f"Treasury API raw response: {latest_record}")

        curve = {}
        for field, maturity in self.FIELD_MAPPING.items():
            val = latest_record.get(field)
            if val is None or val == "null" or str(val).strip() == "":
                continue
            # Treasury yields are strings representing percentages (e.g., "4.25")
            # Convert to decimal by dividing by 100
            try:
                curve[maturity] = float(val) / 100.0
            except ValueError as e:
                raise DataNormalizationError(f"Could not convert Treasury value '{val}' for {field} to float") from e  # noqa: E501

        if not curve:
            raise DataNormalizationError("No valid yields found in Treasury API response.")  # noqa: E501

        return curve
