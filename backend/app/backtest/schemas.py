"""Backtest request/response schemas."""
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# =============================================================================
# Strategy Names
# =============================================================================

STRATEGY_NAMES = Literal[
    "vwap_ma_volume",
    "sma_crossover",
    "rsi",
    "macd",
    "bollinger_bands",
]


# =============================================================================
# Backtest Request/Response
# =============================================================================

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
    strategy_name: STRATEGY_NAMES = Field(
        default="vwap_ma_volume",
        description="Strategy to use for backtesting"
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
    heatmap: Optional["HeatmapResult"] = None
    paper_trade: Optional["PaperTradeResult"] = None


# =============================================================================
# Parameter Heatmap
# =============================================================================

class HeatmapRequest(BaseModel):
    """Heatmap optimization request parameters."""
    ticker: str = Field(..., description="Stock ticker symbol")
    timeframe: str = Field(default="60min", description="Candle interval")
    start_date: date = Field(..., description="Start date")
    end_date: date = Field(..., description="End date")
    starting_capital: float = Field(default=10000.0, ge=100.0)
    slippage: float = Field(default=0.1, ge=0.0, le=5.0)
    commission: float = Field(default=1.0, ge=0.0, le=50.0)
    position_type: Literal["fixed", "percent"] = Field(default="percent")
    lot_size: int = Field(default=50, ge=1)
    percent_capital: float = Field(default=10.0, ge=1.0, le=100.0)
    strategy_direction: Literal["long", "short", "both"] = Field(default="long")
    strategy_name: STRATEGY_NAMES = Field(
        default="vwap_ma_volume",
        description="Strategy to use for optimization"
    )
    # Optional custom parameter ranges
    take_profit_values: Optional[list[float]] = Field(
        default=None,
        description="Custom take profit values (percentages). Default: [1, 2, 4, 6, 8, 10]"
    )
    stop_loss_values: Optional[list[float]] = Field(
        default=None,
        description="Custom stop loss values (percentages). Default: [0.5, 1, 2, 3, 4, 5]"
    )


class HeatmapPoint(BaseModel):
    """Single point in the parameter heatmap."""
    take_profit: float = Field(..., description="Take profit percentage")
    stop_loss: float = Field(..., description="Stop loss percentage")
    return_pct: float = Field(..., description="Total return percentage")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    win_rate: float = Field(..., description="Win rate percentage")
    max_drawdown: float = Field(..., description="Maximum drawdown percentage")
    total_trades: int = Field(..., description="Number of trades")


class HeatmapResult(BaseModel):
    """Parameter heatmap optimization results."""
    take_profit_values: list[float] = Field(..., description="X-axis values")
    stop_loss_values: list[float] = Field(..., description="Y-axis values")
    heatmap_data: list[HeatmapPoint] = Field(..., description="Grid of results")
    best_take_profit: float = Field(..., description="Best take profit parameter")
    best_stop_loss: float = Field(..., description="Best stop loss parameter")
    best_return: float = Field(..., description="Return at best parameters")
    total_backtests: int = Field(..., description="Total number of backtests run")


# =============================================================================
# Paper Trading
# =============================================================================

class PaperTradeRequest(BaseModel):
    """Paper trading request parameters."""
    ticker: str = Field(..., description="Stock ticker symbol")
    timeframe: str = Field(default="60min", description="Candle interval")
    days: int = Field(default=30, ge=1, le=365, description="Days of historical data")
    risk_per_trade: float = Field(default=2.0, ge=0.1, le=10.0)
    stop_loss: float = Field(default=2.0, ge=0.1, le=20.0)
    take_profit: float = Field(default=4.0, ge=0.1, le=50.0)
    position_type: Literal["fixed", "percent"] = Field(default="percent")
    lot_size: int = Field(default=50, ge=1)
    percent_capital: float = Field(default=10.0, ge=1.0, le=100.0)
    starting_capital: float = Field(default=10000.0, ge=100.0)
    slippage: float = Field(default=0.1, ge=0.0, le=5.0)
    commission: float = Field(default=1.0, ge=0.0, le=50.0)
    strategy_direction: Literal["long", "short", "both"] = Field(default="long")
    strategy_name: STRATEGY_NAMES = Field(
        default="vwap_ma_volume",
        description="Strategy to use for paper trading"
    )


class PaperTradePosition(BaseModel):
    """Current paper trade position."""
    ticker: str = Field(..., description="Stock ticker symbol")
    direction: Literal["LONG", "SHORT"] = Field(..., description="Position direction")
    size: int = Field(..., description="Position size (shares)")
    entry_price: float = Field(..., description="Entry price")
    current_price: float = Field(..., description="Current market price")
    unrealized_pnl: float = Field(..., description="Unrealized P&L in dollars")
    unrealized_pnl_pct: float = Field(..., description="Unrealized P&L percentage")
    entry_date: datetime = Field(..., description="Entry timestamp")


class PaperTradeHistoryItem(BaseModel):
    """Single paper trade history item."""
    entry_date: datetime
    exit_date: datetime
    direction: Literal["LONG", "SHORT"]
    size: int
    entry_price: float
    exit_price: float
    pnl: float
    pnl_pct: float


class PaperTradeResult(BaseModel):
    """Paper trading session result."""
    session_id: str = Field(..., description="Unique session identifier")
    ticker: str = Field(..., description="Stock ticker symbol")
    strategy_name: str = Field(..., description="Strategy being used")
    start_date: datetime = Field(..., description="Session start date")
    end_date: datetime = Field(..., description="Session end date")
    starting_capital: float = Field(..., description="Initial capital")
    current_capital: float = Field(..., description="Current capital value")
    current_position: Optional[PaperTradePosition] = Field(
        default=None, description="Current open position if any"
    )
    realized_pnl: float = Field(..., description="Realized P&L from closed trades")
    realized_pnl_pct: float = Field(..., description="Realized P&L percentage")
    unrealized_pnl: float = Field(..., description="Unrealized P&L from open position")
    total_pnl: float = Field(..., description="Total P&L (realized + unrealized)")
    total_trades: int = Field(..., description="Total number of completed trades")
    trade_history: list[PaperTradeHistoryItem] = Field(
        default_factory=list, description="History of completed trades"
    )
    is_active: bool = Field(default=True, description="Whether session is still active")
    last_updated: datetime = Field(..., description="Last update timestamp")


# =============================================================================
# Strategy Info
# =============================================================================

class StrategyInfo(BaseModel):
    """Information about a trading strategy."""
    name: str = Field(..., description="Strategy identifier")
    display_name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Strategy description")
    indicators: list[str] = Field(..., description="Indicators used")
    entry_logic: str = Field(..., description="Entry signal logic")
    exit_logic: str = Field(..., description="Exit signal logic")


class StrategiesResponse(BaseModel):
    """Response containing available strategies."""
    strategies: list[StrategyInfo]


# Forward references for circular dependencies
BacktestResponse.model_rebuild()
