"""Pydantic schemas for data models."""
from datetime import datetime
from pydantic import BaseModel


class OHLCVBar(BaseModel):
    """Single OHLCV bar."""
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockData(BaseModel):
    """Stock data response."""
    ticker: str
    timeframe: str
    bars: list[OHLCVBar]
