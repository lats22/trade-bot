"""Alpha Vantage API client for fetching stock data."""
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

from app.data.schemas import OHLCVBar, StockData

CACHE_DIR = Path("/app/data/cache")


class AlphaVantageClient:
    """Client for Alpha Vantage API."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self):
        self.api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY not set")
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, ticker: str, timeframe: str) -> Path:
        """Get cache file path."""
        return CACHE_DIR / f"{ticker}_{timeframe}_daily.csv"

    def _fetch_daily(self, ticker: str) -> pd.DataFrame:
        """Fetch daily data from API (free tier - last 100 days)."""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "outputsize": "compact",
            "apikey": self.api_key,
        }
        response = requests.get(self.BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        time_series_key = "Time Series (Daily)"
        if time_series_key not in data:
            if "Note" in data:
                raise ValueError(f"API limit reached: {data['Note']}")
            if "Error Message" in data:
                raise ValueError(f"API error: {data['Error Message']}")
            if "Information" in data:
                raise ValueError(f"API info: {data['Information']}")
            raise ValueError(f"Unexpected response: {data}")

        records = []
        for dt_str, values in data[time_series_key].items():
            records.append({
                "datetime": dt_str,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": int(values["5. volume"]),
            })

        df = pd.DataFrame(records)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime").reset_index(drop=True)
        return df

    def get_intraday_data(
        self,
        ticker: str,
        interval: str,
        start_date: datetime,
        end_date: datetime,
    ) -> StockData:
        """
        Get daily data for a ticker (free tier uses daily data).

        Args:
            ticker: Stock symbol (e.g., "AAPL")
            interval: Ignored for free tier, uses daily data
            start_date: Start of date range
            end_date: End of date range

        Returns:
            StockData with OHLCV bars
        """
        cache_path = self._get_cache_path(ticker, "daily")

        # Check cache freshness (refresh if older than 1 day)
        use_cache = False
        if cache_path.exists():
            cache_age = datetime.now().timestamp() - cache_path.stat().st_mtime
            if cache_age < 86400:  # 24 hours
                use_cache = True

        if use_cache:
            df = pd.read_csv(cache_path, parse_dates=["datetime"])
        else:
            df = self._fetch_daily(ticker)
            df.to_csv(cache_path, index=False)

        # Filter to date range
        df = df[
            (df["datetime"] >= pd.Timestamp(start_date))
            & (df["datetime"] <= pd.Timestamp(end_date))
        ]
        df = df.drop_duplicates(subset=["datetime"])
        df = df.sort_values("datetime").reset_index(drop=True)

        bars = [
            OHLCVBar(
                datetime=row["datetime"],
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"],
            )
            for _, row in df.iterrows()
        ]

        return StockData(ticker=ticker, timeframe="daily", bars=bars)
