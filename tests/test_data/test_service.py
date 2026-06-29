import datetime

import pytest

from src.data.base import DataFetcher
from src.data.exceptions import DataFetchError
from src.data.service import MarketDataService
from src.utils.cache import JSONCache


class DummyFetcher(DataFetcher):
    def __init__(self, name, should_fail=False):  # noqa: D107
        self.name = name
        self.should_fail = should_fail

    def fetch_yield_curve(self, date: datetime.date):  # noqa: ARG002
        if self.should_fail:
            raise DataFetchError(f"{self.name} failed")
        return {1.0: 0.05}


def test_market_data_service_success():
    fetcher1 = DummyFetcher("F1", should_fail=True)
    fetcher2 = DummyFetcher("F2", should_fail=False)

    service = MarketDataService(fetchers=[fetcher1, fetcher2])

    # F1 fails, should fall back to F2
    curve = service.fetch_yield_curve(datetime.date(2023, 1, 5))
    assert curve == {1.0: 0.05}


def test_market_data_service_all_fail():
    fetcher1 = DummyFetcher("F1", should_fail=True)
    fetcher2 = DummyFetcher("F2", should_fail=True)

    service = MarketDataService(fetchers=[fetcher1, fetcher2])

    with pytest.raises(DataFetchError, match="All data fetchers failed"):
        service.fetch_yield_curve(datetime.date(2023, 1, 5))


def test_market_data_service_with_cache(tmp_path):
    cache = JSONCache(cache_dir=str(tmp_path / ".cache"))
    fetcher1 = DummyFetcher("F1", should_fail=False)

    service = MarketDataService(fetchers=[fetcher1], cache=cache)
    date = datetime.date(2023, 1, 5)

    # First call goes to fetcher and caches
    curve = service.fetch_yield_curve(date)
    assert curve == {1.0: 0.05}

    # Modify fetcher to fail, but it shouldn't be called because it's cached
    fetcher1.should_fail = True
    curve2 = service.fetch_yield_curve(date)
    assert curve2 == {1.0: 0.05}
