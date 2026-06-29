import datetime  # noqa: D100
from abc import ABC, abstractmethod


class DataFetcher(ABC):
    """Abstract base class for market data fetchers."""

    @abstractmethod
    def fetch_yield_curve(self, date: datetime.date) -> dict[float, float]:
        """Fetch the yield curve for a given date.

        Args:
            date: The business date to fetch yields for.

        Returns:
            A dictionary mapping maturity in years (float) to the yield in decimal format (e.g., 0.0425 for 4.25%).
            
        Raises:
            DataFetchError: If the source API fails or is unreachable.
            MarketHolidayError: If the requested date is a holiday/weekend and no valid data exists.
            DataNormalizationError: If the data cannot be parsed into the expected format.

        """  # noqa: E501, W293
        pass
