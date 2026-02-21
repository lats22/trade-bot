"""Backtest API endpoints."""
import logging
import traceback
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.backtest.runner import run_backtest, get_strategy_class, STRATEGY_REGISTRY
from app.backtest.schemas import (
    BacktestRequest,
    BacktestResponse,
    HeatmapRequest,
    HeatmapResult,
    PaperTradeRequest,
    PaperTradeResult,
    StrategyInfo,
    StrategiesResponse,
)
from app.backtest.parameter_heatmap import run_parameter_heatmap
from app.backtest.paper_trading import (
    run_paper_trade_simulation,
    get_paper_trade_status,
    list_paper_trade_sessions,
    stop_paper_trade,
    get_recent_data,
)
from app.data.alpha_vantage import AlphaVantageClient
import pandas as pd

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Strategy Descriptions
# =============================================================================

STRATEGY_DESCRIPTIONS = {
    "vwap_ma_volume": StrategyInfo(
        name="vwap_ma_volume",
        display_name="VWAP + MA + Volume",
        description="Combines VWAP, Moving Average, and Volume indicators to identify high-probability entries when price is trending with volume confirmation.",
        indicators=["VWAP", "SMA (20)", "Volume SMA"],
        entry_logic="LONG: Price above VWAP and MA with volume spike. SHORT: Price below VWAP and MA with volume spike.",
        exit_logic="Stop loss or take profit hit.",
    ),
    "sma_crossover": StrategyInfo(
        name="sma_crossover",
        display_name="SMA Crossover",
        description="Classic moving average crossover strategy that generates signals when fast MA crosses slow MA.",
        indicators=["SMA (10)", "SMA (30)"],
        entry_logic="LONG: Fast MA crosses above Slow MA (golden cross). SHORT: Fast MA crosses below Slow MA (death cross).",
        exit_logic="Stop loss, take profit, or opposite crossover signal.",
    ),
    "rsi": StrategyInfo(
        name="rsi",
        display_name="RSI Overbought/Oversold",
        description="Mean reversion strategy using RSI to identify oversold (buy) and overbought (sell) conditions.",
        indicators=["RSI (14)"],
        entry_logic="LONG: RSI crosses above 30 (oversold bounce). SHORT: RSI crosses below 70 (overbought drop).",
        exit_logic="Stop loss, take profit, or RSI reaches opposite extreme.",
    ),
    "macd": StrategyInfo(
        name="macd",
        display_name="MACD Signal Crossover",
        description="Momentum strategy using MACD line crossing signal line to identify trend changes.",
        indicators=["MACD (12, 26, 9)"],
        entry_logic="LONG: MACD crosses above Signal line. SHORT: MACD crosses below Signal line.",
        exit_logic="Stop loss, take profit, or opposite crossover.",
    ),
    "bollinger_bands": StrategyInfo(
        name="bollinger_bands",
        display_name="Bollinger Bands",
        description="Mean reversion strategy that trades bounces off Bollinger Band extremes.",
        indicators=["Bollinger Bands (20, 2)"],
        entry_logic="LONG: Price touches lower band. SHORT: Price touches upper band.",
        exit_logic="Stop loss, take profit, or price reaches middle band.",
    ),
}


# =============================================================================
# Backtest Endpoints
# =============================================================================

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
        logger.error(f"Backtest error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


# =============================================================================
# Parameter Heatmap Endpoints
# =============================================================================

@router.post("/backtest/heatmap", response_model=HeatmapResult)
async def create_heatmap(request: HeatmapRequest) -> HeatmapResult:
    """
    Run parameter optimization grid search.

    Tests combinations of take_profit and stop_loss values to find optimal parameters.
    Returns a heatmap of results for each parameter combination.
    """
    try:
        # Fetch data
        client = AlphaVantageClient()
        stock_data = client.get_intraday_data(
            ticker=request.ticker,
            interval=request.timeframe,
            start_date=datetime.combine(request.start_date, datetime.min.time()),
            end_date=datetime.combine(request.end_date, datetime.max.time()),
        )

        if not stock_data.bars:
            raise ValueError(f"No data found for {request.ticker}")

        # Convert to DataFrame
        df = pd.DataFrame([
            {
                "datetime": bar.datetime,
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
            for bar in stock_data.bars
        ])
        df.set_index("datetime", inplace=True)

        # Get strategy class
        strategy_class = get_strategy_class(request.strategy_name)

        # Run heatmap optimization
        result = run_parameter_heatmap(
            df=df,
            strategy_class=strategy_class,
            request=request,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Heatmap error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Heatmap optimization failed: {str(e)}")


# =============================================================================
# Paper Trading Endpoints
# =============================================================================

@router.post("/paper-trade/start", response_model=PaperTradeResult)
async def start_paper_trade(request: PaperTradeRequest) -> PaperTradeResult:
    """
    Start a new paper trading session.

    Uses recent historical data to simulate live trading with the specified strategy.
    """
    try:
        # Fetch recent data
        df = get_recent_data(
            ticker=request.ticker,
            days=request.days,
            interval=request.timeframe,
        )

        # Get strategy class
        strategy_class = get_strategy_class(request.strategy_name)

        # Run paper trade simulation
        result = run_paper_trade_simulation(
            df=df,
            strategy_class=strategy_class,
            request=request,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Paper trade error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Paper trading failed: {str(e)}")


@router.get("/paper-trade/status/{session_id}", response_model=PaperTradeResult)
async def get_paper_trade_status_endpoint(session_id: str) -> PaperTradeResult:
    """
    Get the current status of a paper trading session.
    """
    result = get_paper_trade_status(session_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    return result


@router.get("/paper-trade/sessions", response_model=list[PaperTradeResult])
async def list_paper_trade_sessions_endpoint() -> list[PaperTradeResult]:
    """
    List all paper trading sessions.
    """
    return list_paper_trade_sessions()


@router.post("/paper-trade/stop/{session_id}", response_model=PaperTradeResult)
async def stop_paper_trade_endpoint(session_id: str) -> PaperTradeResult:
    """
    Stop an active paper trading session.
    """
    result = stop_paper_trade(session_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    return result


# =============================================================================
# Strategy Endpoints
# =============================================================================

@router.get("/strategies", response_model=StrategiesResponse)
async def list_strategies() -> StrategiesResponse:
    """
    List all available trading strategies.
    """
    strategies = [
        STRATEGY_DESCRIPTIONS[name]
        for name in STRATEGY_REGISTRY.keys()
        if name in STRATEGY_DESCRIPTIONS
    ]
    return StrategiesResponse(strategies=strategies)


@router.get("/strategies/{strategy_name}", response_model=StrategyInfo)
async def get_strategy(strategy_name: str) -> StrategyInfo:
    """
    Get details about a specific strategy.
    """
    if strategy_name not in STRATEGY_DESCRIPTIONS:
        raise HTTPException(
            status_code=404,
            detail=f"Strategy not found: {strategy_name}. Available: {list(STRATEGY_DESCRIPTIONS.keys())}"
        )
    return STRATEGY_DESCRIPTIONS[strategy_name]


# =============================================================================
# Ticker Endpoints
# =============================================================================

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
