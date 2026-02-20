"""Alpha Vantage API client for fetching stock data."""
import os
from datetime import datetime, timedelta
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

    def _get_cache_path(self, ticker: str, timeframe: str, month: str) -> Path:
        """Get cache file path."""
        return CACHE_DIR / f"{ticker}_{timeframe}_{month}.csv"

    def _fetch_intraday(
        self, ticker: str, interval: str, month: str
    ) -> pd.DataFrame:
        """Fetch intraday data from API."""
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": ticker,
            "interval": interval,
            "month": month,
            "outputsize": "full",
            "apikey": self.api_key,
        }
        response = requests.get(self.BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        time_series_key = f"Time Series ({interval})"
        if time_series_key not in data:
            if "Note" in data:
                raise ValueError(f"API limit reached: {data['Note']}")
            if "Error Message" in data:
                raise ValueError(f"API error: {data['Error Message']}")
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
        Get intraday data for a ticker.

        Args:
            ticker: Stock symbol (e.g., "AAPL")
            interval: Candle interval ("15min", "30min", "60min")
            start_date: Start of date range
            end_date: End of date range

        Returns:
            StockData with OHLCV bars
        """
        all_bars = []

        # Alpha Vantage uses month format YYYY-MM
        current = start_date.replace(day=1)
        end_month = end_date.replace(day=1)

        while current <= end_month:
            month_str = current.strftime("%Y-%m")
            cache_path = self._get_cache_path(ticker, interval, month_str)

            if cache_path.exists():
                df = pd.read_csv(cache_path, parse_dates=["datetime"])
            else:
                df = self._fetch_intraday(ticker, interval, month_str)
                df.to_csv(cache_path, index=False)

            all_bars.append(df)

            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        if not all_bars:
            return StockData(ticker=ticker, timeframe=interval, bars=[])

        combined = pd.concat(all_bars, ignore_index=True)
        combined = combined[
            (combined["datetime"] >= start_date)
            & (combined["datetime"] <= end_date)
        ]
        combined = combined.drop_duplicates(subset=["datetime"])
        combined = combined.sort_values("datetime").reset_index(drop=True)

        bars = [
            OHLCVBar(
                datetime=row["datetime"],
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"],
            )
            for _, row in combined.iterrows()
        ]

        return StockData(ticker=ticker, timeframe=interval, bars=bars)
