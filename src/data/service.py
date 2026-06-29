import datetime  # noqa: D100
import logging

from src.utils.cache import JSONCache

from .base import DataFetcher
from .exceptions import DataFetchError, MarketHolidayError

logger = logging.getLogger(__name__)


class MarketDataService:
    """Orchestrator for fetching market data.
    Provides automatic failover across multiple data fetchers and caching.
    """  # noqa: D205

    def __init__(self, fetchers: list[DataFetcher], cache: JSONCache | None = None):
        """Args:
        fetchers: A list of DataFetcher instances, ordered by priority.
        cache: An optional JSONCache instance to cache results.

        """  # noqa: D205
        if not fetchers:
            raise ValueError("At least one DataFetcher must be provided.")
        self.fetchers = fetchers
        self.cache = cache

    def fetch_yield_curve(self, date: datetime.date) -> dict[float, float]:
        """Fetch the yield curve for a given date, trying fetchers in order.
        Uses cache if available.
        """  # noqa: D205
        # We cache by the string representation of the date
        date_str = date.strftime("%Y-%m-%d")
        cache_key = f"yield_curve_{date_str}"

        if self.cache is not None:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                # Convert string keys back to float (JSON keys are always strings)
                logger.debug(f"Cache hit for {cache_key}")
                return {float(k): float(v) for k, v in cached_data.items()}

        # If not cached, try fetchers in order
        errors = []
        for fetcher in self.fetchers:
            fetcher_name = fetcher.__class__.__name__
            try:
                logger.info(
                    f"Attempting to fetch yield curve for {date} using {fetcher_name}"
                )  # noqa: E501
                curve = fetcher.fetch_yield_curve(date)

                # Save to cache if successful
                if self.cache is not None:
                    # JSON cache needs keys to be strings
                    serializable_curve = {str(k): v for k, v in curve.items()}
                    self.cache.set(cache_key, serializable_curve)

                logger.info(f"Successfully fetched yield curve using {fetcher_name}")
                return curve

            except (DataFetchError, MarketHolidayError) as e:
                logger.warning(f"{fetcher_name} failed to fetch data for {date}: {e}")
                errors.append(f"{fetcher_name}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in {fetcher_name}: {e}")
                errors.append(f"{fetcher_name}: {e}")

        # If all fetchers fail, raise an error
        error_msg = "All data fetchers failed:\n" + "\n".join(errors)
        logger.error(error_msg)
        raise DataFetchError(error_msg)
