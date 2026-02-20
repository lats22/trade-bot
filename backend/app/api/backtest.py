"""Backtest API endpoints."""
from fastapi import APIRouter, HTTPException

from app.backtest.runner import run_backtest
from app.backtest.schemas import BacktestRequest, BacktestResponse

router = APIRouter()


@router.post("/backtest", response_model=BacktestResponse)
async def create_backtest(request: BacktestRequest) -> BacktestResponse:
    """
    Run a backtest with the given parameters.

    Returns metrics, equity curve, and trade log.
    """
    try:
        result = run_backtest(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@router.get("/tickers")
async def list_tickers():
    """
    List popular stock tickers.

    Note: Alpha Vantage supports any US stock ticker.
    """
    return {
        "popular": [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corporation"},
            {"symbol": "GOOGL", "name": "Alphabet Inc."},
            {"symbol": "AMZN", "name": "Amazon.com Inc."},
            {"symbol": "TSLA", "name": "Tesla Inc."},
            {"symbol": "NVDA", "name": "NVIDIA Corporation"},
            {"symbol": "META", "name": "Meta Platforms Inc."},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
        ]
    }
