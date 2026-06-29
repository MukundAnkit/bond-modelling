class DataFetchError(Exception):  # noqa: D100
    """Raised when a data fetcher fails to retrieve data from its source."""

    pass


class DataNormalizationError(Exception):
    """Raised when data retrieved from a source cannot be correctly normalized."""

    pass


class MarketHolidayError(Exception):
    """Raised when data is requested for a market holiday or weekend and no fallback interpolation applies."""  # noqa: E501

    pass
