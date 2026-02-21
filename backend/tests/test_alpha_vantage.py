"""Tests for Alpha Vantage client."""
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from app.data.alpha_vantage import AlphaVantageClient


@pytest.fixture
def mock_api_key():
    """Set mock API key."""
    with patch.dict(os.environ, {"ALPHA_VANTAGE_API_KEY": "test_key"}):
        yield


@pytest.fixture
def mock_response():
    """Mock API response."""
    return {
        "Time Series (Daily)": {
            "2024-01-02 10:00:00": {
                "1. open": "100.00",
                "2. high": "101.00",
                "3. low": "99.00",
                "4. close": "100.50",
                "5. volume": "1000000",
            },
            "2024-01-02 11:00:00": {
                "1. open": "100.50",
                "2. high": "102.00",
                "3. low": "100.00",
                "4. close": "101.50",
                "5. volume": "1200000",
            },
        }
    }


def test_client_requires_api_key():
    """Test client raises error without API key."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("ALPHA_VANTAGE_API_KEY", None)
        with pytest.raises(ValueError, match="ALPHA_VANTAGE_API_KEY not set"):
            AlphaVantageClient()


def test_fetch_intraday_parses_response(mock_api_key, mock_response, tmp_path):
    """Test API response is parsed correctly."""
    with patch("app.data.alpha_vantage.CACHE_DIR", tmp_path):
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: mock_response,
            )

            client = AlphaVantageClient()
            data = client.get_intraday_data(
                ticker="AAPL",
                interval="60min",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 31),
            )

            assert data.ticker == "AAPL"
            assert data.timeframe == "daily"  # Free tier uses daily data
            assert len(data.bars) == 2
            assert data.bars[0].close == 100.50
            assert data.bars[1].close == 101.50
