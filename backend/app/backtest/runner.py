"""Backtest runner using Backtrader."""
from datetime import datetime
import math

import backtrader as bt
import pandas as pd

from app.backtest.schemas import (
    BacktestRequest,
    BacktestResponse,
    BacktestMetrics,
    EquityPoint,
    TradeRecord,
)
from app.data.alpha_vantage import AlphaVantageClient
from app.strategies.vwap_ma_volume import VWAPMAVolumeStrategy


class EquityObserver(bt.Observer):
    """Observer to track equity over time."""

    lines = ("equity",)

    def next(self):
        self.lines.equity[0] = self._owner.broker.getvalue()


def calculate_metrics(
    initial_capital: float,
    final_capital: float,
    trades: list[dict],
    equity_values: list[float],
) -> BacktestMetrics:
    """Calculate performance metrics."""
    total_return = ((final_capital - initial_capital) / initial_capital) * 100

    if not trades:
        return BacktestMetrics(
            total_return=total_return,
            win_rate=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            total_trades=0,
            profit_factor=0.0,
            risk_reward_ratio=0.0,
            best_streak=0,
            worst_streak=0,
        )

    # Win rate
    wins = [t for t in trades if t["pnl"] > 0]
    losses = [t for t in trades if t["pnl"] <= 0]
    win_rate = (len(wins) / len(trades)) * 100 if trades else 0.0

    # Profit factor
    gross_profit = sum(t["pnl"] for t in wins) if wins else 0.0
    gross_loss = abs(sum(t["pnl"] for t in losses)) if losses else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

    # Risk/Reward ratio
    avg_win = sum(t["pnl"] for t in wins) / len(wins) if wins else 0.0
    avg_loss = abs(sum(t["pnl"] for t in losses) / len(losses)) if losses else 0.0
    risk_reward = avg_win / avg_loss if avg_loss > 0 else 0.0

    # Max drawdown
    peak = initial_capital
    max_dd = 0.0
    for equity in equity_values:
        if equity > peak:
            peak = equity
        dd = (peak - equity) / peak * 100
        if dd > max_dd:
            max_dd = dd

    # Sharpe ratio (simplified - assumes risk-free rate of 0)
    if len(equity_values) > 1:
        returns = pd.Series(equity_values).pct_change().dropna()
        if returns.std() > 0:
            sharpe = (returns.mean() / returns.std()) * math.sqrt(252)
        else:
            sharpe = 0.0
    else:
        sharpe = 0.0

    # Win/Loss streaks
    best_streak = 0
    worst_streak = 0
    current_win = 0
    current_loss = 0
    for t in trades:
        if t["pnl"] > 0:
            current_win += 1
            current_loss = 0
            best_streak = max(best_streak, current_win)
        else:
            current_loss += 1
            current_win = 0
            worst_streak = max(worst_streak, current_loss)

    return BacktestMetrics(
        total_return=round(total_return, 2),
        win_rate=round(win_rate, 1),
        max_drawdown=round(-max_dd, 2),
        sharpe_ratio=round(sharpe, 2),
        total_trades=len(trades),
        profit_factor=round(profit_factor, 2),
        risk_reward_ratio=round(risk_reward, 2),
        best_streak=best_streak,
        worst_streak=worst_streak,
    )


def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """
    Run backtest with given parameters.

    Args:
        request: Backtest configuration

    Returns:
        BacktestResponse with metrics, equity curve, and trades
    """
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

    # Setup Backtrader
    cerebro = bt.Cerebro()

    # Add data feed
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)

    # Add strategy
    cerebro.addstrategy(
        VWAPMAVolumeStrategy,
        stop_loss=request.stop_loss / 100,
        take_profit=request.take_profit / 100,
        risk_per_trade=request.risk_per_trade / 100,
        position_type=request.position_type,
        lot_size=request.lot_size,
        percent_capital=request.percent_capital / 100,
    )

    # Broker settings
    cerebro.broker.setcash(request.starting_capital)
    cerebro.broker.setcommission(commission=request.commission)
    cerebro.broker.set_slippage_perc(request.slippage / 100)

    # Run backtest
    results = cerebro.run()
    strategy = results[0]

    # Extract equity curve from broker value
    final_capital = cerebro.broker.getvalue()

    # Simple equity curve based on trades
    equity_values = [request.starting_capital]
    equity_curve = [EquityPoint(datetime=df.index[0], equity=request.starting_capital)]

    current_equity = request.starting_capital
    for trade in strategy.trades:
        current_equity += trade["pnl"]
        equity_values.append(current_equity)
        equity_curve.append(EquityPoint(
            datetime=trade["exit_date"],
            equity=current_equity
        ))

    # Add final point
    if df.index[-1] != equity_curve[-1].datetime:
        equity_values.append(final_capital)
        equity_curve.append(EquityPoint(datetime=df.index[-1], equity=final_capital))

    # Calculate drawdown curve
    drawdown_curve = []
    peak = request.starting_capital
    for point in equity_curve:
        if point.equity > peak:
            peak = point.equity
        dd = ((peak - point.equity) / peak) * 100
        drawdown_curve.append(EquityPoint(datetime=point.datetime, equity=-dd))

    # Convert trades
    trades = [
        TradeRecord(
            entry_date=t["entry_date"],
            exit_date=t["exit_date"],
            entry_price=t["entry_price"],
            exit_price=t["exit_price"],
            size=t["size"],
            pnl=round(t["pnl"], 2),
            pnl_percent=round(t["pnl_percent"], 2),
        )
        for t in strategy.trades
    ]

    # Calculate metrics
    final_capital = cerebro.broker.getvalue()
    metrics = calculate_metrics(
        request.starting_capital,
        final_capital,
        strategy.trades,
        equity_values,
    )

    return BacktestResponse(
        request=request,
        metrics=metrics,
        equity_curve=equity_curve,
        drawdown_curve=drawdown_curve,
        trades=trades,
    )
