"""Backtest request/response schemas."""
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    """Backtest request parameters."""
    ticker: str = Field(..., description="Stock ticker symbol")
    timeframe: str = Field(default="60min", description="Candle interval")
    start_date: date = Field(..., description="Start date")
    end_date: date = Field(..., description="End date")
    risk_per_trade: float = Field(default=2.0, ge=0.1, le=10.0)
    stop_loss: float = Field(default=2.0, ge=0.1, le=20.0)
    take_profit: float = Field(default=4.0, ge=0.1, le=50.0)
    position_type: Literal["fixed", "percent"] = Field(default="percent")
    lot_size: int = Field(default=50, ge=1)
    percent_capital: float = Field(default=10.0, ge=1.0, le=100.0)
    starting_capital: float = Field(default=10000.0, ge=100.0)
    slippage: float = Field(default=0.1, ge=0.0, le=5.0)
    commission: float = Field(default=1.0, ge=0.0, le=50.0)
    strategy_direction: Literal["long", "short", "both"] = Field(
        default="long", description="Trading direction: long, short, or both"
    )


class TradeRecord(BaseModel):
    """Single trade record."""
    entry_date: datetime
    exit_date: datetime
    entry_price: float
    exit_price: float
    size: int
    pnl: float
    pnl_percent: float
    trade_type: Literal["LONG", "SHORT"] = "LONG"


class BacktestMetrics(BaseModel):
    """Backtest performance metrics."""
    total_return: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    total_trades: int
    profit_factor: float
    risk_reward_ratio: float
    best_streak: int
    worst_streak: int


class EquityPoint(BaseModel):
    """Single equity curve point."""
    datetime: datetime
    equity: float


class MonteCarloResult(BaseModel):
    """Monte Carlo simulation results."""
    simulations: int
    median_return: float
    best_return: float
    worst_return: float
    percentile_5: float
    percentile_95: float
    median_max_drawdown: float
    worst_max_drawdown: float
    return_distribution: dict


class WalkForwardWindow(BaseModel):
    """Single walk-forward window result."""
    window: int
    start_date: str
    end_date: str
    train_end_date: str
    test_start_date: str
    train_size: int
    test_size: int
    return_pct: float
    profitable: bool


class WalkForwardResult(BaseModel):
    """Walk-forward analysis results."""
    num_windows: int
    windows: list[WalkForwardWindow]
    overall_consistency: float
    avg_return: float
    profitable_windows: int
    train_pct: float


class BacktestResponse(BaseModel):
    """Backtest results."""
    request: BacktestRequest
    metrics: BacktestMetrics
    equity_curve: list[EquityPoint]
    drawdown_curve: list[EquityPoint]
    trades: list[TradeRecord]
    monte_carlo: Optional[MonteCarloResult] = None
    walk_forward: Optional[WalkForwardResult] = None
