import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from requests.exceptions import RequestException

from src.data.corporate import CorporateFetcher
from src.data.exceptions import (
    DataFetchError,
    DataNormalizationError,
)
from src.data.finra import MockFinraFetcher
from src.data.fred import FredFetcher
from src.data.global_sovereign import GlobalSovereignFetcher
from src.data.sofr import SofrFetcher
from src.data.treasury import TreasuryFetcher
from src.data.yfinance_fetcher import YFinanceFetcher


def test_fred_fetcher_success():
    fetcher = FredFetcher()
    test_date = datetime.date(2023, 1, 5)

    # Mock dataframe returned by pandas_datareader
    mock_df = pd.DataFrame(
        {
            "DGS3MO": [4.25, 4.26],
            "DGS1": [4.50, 4.51],
            "DGS2": [4.30, 4.30],
            "DGS5": [3.80, 3.82],
            "DGS10": [3.60, 3.65],
            "DGS30": [3.70, 3.75],
        },
        index=pd.to_datetime(["2023-01-04", "2023-01-05"]),
    )

    with patch("src.data.fred.web.DataReader", return_value=mock_df):
        curve = fetcher.fetch_yield_curve(test_date)

    assert curve[0.25] == 0.0426
    assert curve[1.0] == 0.0451
    assert curve[10.0] == 0.0365


def test_fred_fetcher_api_error():
    fetcher = FredFetcher()
    with patch(
        "src.data.fred.web.DataReader", side_effect=RequestException("API down")
    ):  # noqa: E501, SIM117
        with pytest.raises(DataFetchError, match="FRED fetch failed"):
            fetcher.fetch_yield_curve(datetime.date(2023, 1, 5))


def test_yfinance_fetcher_success():
    fetcher = YFinanceFetcher()
    test_date = datetime.date(2023, 1, 5)

    # yfinance returns multi-index columns if downloading multiple tickers, but we only care about 'Close'  # noqa: E501
    mock_close_df = pd.DataFrame(
        {"^IRX": [42.5], "^FVX": [38.2], "^TNX": [36.5], "^TYX": [37.5]},
        index=pd.to_datetime(["2023-01-05"]),
    )

    # Mocking yf.download to return a df with a "Close" column level
    mock_df = pd.DataFrame()
    # Setting up the multi-index is tricky, we can just patch so that df["Close"] returns mock_close_df  # noqa: E501
    # In yfinance, if we download multiple, it's a multiindex.
    mock_df = pd.concat([mock_close_df], axis=1, keys=["Close"])

    with patch("src.data.yfinance_fetcher.yf.download", return_value=mock_df):
        curve = fetcher.fetch_yield_curve(test_date)

    assert curve[0.25] == 0.0425
    assert curve[10.0] == 0.0365


def test_treasury_fetcher_success():
    fetcher = TreasuryFetcher()
    test_date = datetime.date(2023, 1, 5)

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "record_date": "2023-01-05",
                "bc_1month": "4.15",
                "bc_3month": "4.26",
                "bc_10year": "3.65",
            }
        ]
    }

    with patch.object(fetcher.session, "get", return_value=mock_response):
        curve = fetcher.fetch_yield_curve(test_date)

    assert curve[0.25] == 0.0426
    assert curve[10.0] == 0.0365


def test_treasury_fetcher_normalization_error():
    fetcher = TreasuryFetcher()
    test_date = datetime.date(2023, 1, 5)

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [{"record_date": "2023-01-05", "bc_10year": "invalid_number"}]
    }

    with patch.object(fetcher.session, "get", return_value=mock_response):  # noqa: SIM117
        with pytest.raises(DataNormalizationError):
            fetcher.fetch_yield_curve(test_date)


def test_mock_finra_fetcher():
    base_curve = {1.0: 0.045, 10.0: 0.035}
    # 50 bps spread = +0.005
    fetcher = MockFinraFetcher(base_curve, spread_bps=50.0, is_municipal=False)

    curve = fetcher.fetch_yield_curve(datetime.date.today())
    assert curve[1.0] == pytest.approx(0.050)
    assert curve[10.0] == pytest.approx(0.040)

    # Muni test: 78% of base + spread
    muni_fetcher = MockFinraFetcher(base_curve, spread_bps=50.0, is_municipal=True)
    muni_curve = muni_fetcher.fetch_yield_curve(datetime.date.today())
    assert muni_curve[1.0] == pytest.approx(0.045 * 0.78 + 0.005)


def test_corporate_fetcher_success():
    fetcher = CorporateFetcher(rating="BBB", proxy_maturity=10.0)
    test_date = datetime.date(2023, 1, 5)

    mock_df = pd.DataFrame(
        {"BAMLC0A4CBBBEY": [5.50, 5.55]},
        index=pd.to_datetime(["2023-01-04", "2023-01-05"]),
    )

    with patch("src.data.corporate.web.DataReader", return_value=mock_df):
        curve = fetcher.fetch_yield_curve(test_date)

    assert curve[10.0] == 0.0555


def test_sofr_fetcher_success():
    fetcher = SofrFetcher()
    test_date = datetime.date(2023, 1, 5)

    mock_df = pd.DataFrame(
        {
            "SOFR": [4.30, 4.30],
            "SOFR30DAYAVG": [4.35, 4.36],
            "SOFR90DAYAVG": [4.40, 4.41],
            "SOFR180DAYAVG": [4.45, 4.46],
        },
        index=pd.to_datetime(["2023-01-04", "2023-01-05"]),
    )

    with patch("src.data.sofr.web.DataReader", return_value=mock_df):
        curve = fetcher.fetch_yield_curve(test_date)

    assert curve[1 / 365] == 0.0430
    assert curve[180 / 365] == 0.0446


def test_global_sovereign_fetcher_success():
    fetcher = GlobalSovereignFetcher(region="EUR")
    test_date = datetime.date(2023, 1, 5)

    mock_df = pd.DataFrame(
        {"IRLTLT01EZM156N": [2.50, 2.50]},
        index=pd.to_datetime(["2022-12-01", "2023-01-01"]),
    )

    with patch("src.data.global_sovereign.web.DataReader", return_value=mock_df):
        curve = fetcher.fetch_yield_curve(test_date)

    assert curve[10.0] == 0.0250
