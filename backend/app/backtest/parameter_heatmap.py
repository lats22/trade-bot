"""Parameter heatmap optimization module."""
import logging
import math
from datetime import datetime
from typing import Type

import backtrader as bt
import pandas as pd

from app.backtest.schemas import (
    HeatmapPoint,
    HeatmapResult,
    HeatmapRequest,
)

logger = logging.getLogger(__name__)

# Default parameter ranges
DEFAULT_TAKE_PROFIT_VALUES = [1.0, 2.0, 4.0, 6.0, 8.0, 10.0]  # percentages
DEFAULT_STOP_LOSS_VALUES = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0]  # percentages


def run_single_backtest(
    df: pd.DataFrame,
    strategy_class: Type[bt.Strategy],
    starting_capital: float,
    stop_loss: float,
    take_profit: float,
    slippage: float,
    commission: float,
    position_type: str,
    lot_size: int,
    percent_capital: float,
    strategy_direction: str,
) -> dict:
    """
    Run a single backtest with specific parameters.

    Returns:
        Dictionary with return_pct, sharpe_ratio, win_rate, max_drawdown
    """
    cerebro = bt.Cerebro()

    # Add data feed
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)

    # Add strategy with parameters
    cerebro.addstrategy(
        strategy_class,
        stop_loss=stop_loss / 100,
        take_profit=take_profit / 100,
        position_type=position_type,
        lot_size=lot_size,
        percent_capital=percent_capital / 100,
        strategy_direction=strategy_direction,
    )

    # Broker settings
    cerebro.broker.setcash(starting_capital)
    cerebro.broker.setcommission(commission=commission)
    cerebro.broker.set_slippage_perc(slippage / 100)

    # Run backtest
    results = cerebro.run()
    strategy = results[0]

    # Calculate metrics
    final_capital = cerebro.broker.getvalue()
    return_pct = ((final_capital - starting_capital) / starting_capital) * 100

    trades = strategy.trades
    if not trades:
        return {
            "return_pct": round(return_pct, 2),
            "sharpe_ratio": 0.0,
            "win_rate": 0.0,
            "max_drawdown": 0.0,
            "total_trades": 0,
        }

    # Win rate
    wins = [t for t in trades if t["pnl"] > 0]
    win_rate = (len(wins) / len(trades)) * 100 if trades else 0.0

    # Build equity curve for metrics
    equity_values = [starting_capital]
    current_equity = starting_capital
    for trade in trades:
        current_equity += trade["pnl"]
        equity_values.append(current_equity)

    # Max drawdown
    peak = starting_capital
    max_dd = 0.0
    for equity in equity_values:
        if equity > peak:
            peak = equity
        dd = (peak - equity) / peak * 100
        if dd > max_dd:
            max_dd = dd

    # Sharpe ratio
    if len(equity_values) > 1:
        returns = pd.Series(equity_values).pct_change().dropna()
        if returns.std() > 0:
            sharpe = (returns.mean() / returns.std()) * math.sqrt(252)
        else:
            sharpe = 0.0
    else:
        sharpe = 0.0

    return {
        "return_pct": round(return_pct, 2),
        "sharpe_ratio": round(sharpe, 2),
        "win_rate": round(win_rate, 1),
        "max_drawdown": round(-max_dd, 2),
        "total_trades": len(trades),
    }


def run_parameter_heatmap(
    df: pd.DataFrame,
    strategy_class: Type[bt.Strategy],
    request: HeatmapRequest,
) -> HeatmapResult:
    """
    Run grid search optimization over take_profit and stop_loss parameters.

    Args:
        df: DataFrame with OHLCV data
        strategy_class: Backtrader strategy class to use
        request: Heatmap request parameters

    Returns:
        HeatmapResult with grid of results and best parameters
    """
    take_profit_values = request.take_profit_values or DEFAULT_TAKE_PROFIT_VALUES
    stop_loss_values = request.stop_loss_values or DEFAULT_STOP_LOSS_VALUES

    total_backtests = len(take_profit_values) * len(stop_loss_values)
    logger.info(f"Running parameter heatmap: {total_backtests} backtests")

    heatmap_data = []
    best_point = None
    best_return = float("-inf")

    for tp in take_profit_values:
        for sl in stop_loss_values:
            logger.debug(f"Running backtest: TP={tp}%, SL={sl}%")

            try:
                result = run_single_backtest(
                    df=df,
                    strategy_class=strategy_class,
                    starting_capital=request.starting_capital,
                    stop_loss=sl,
                    take_profit=tp,
                    slippage=request.slippage,
                    commission=request.commission,
                    position_type=request.position_type,
                    lot_size=request.lot_size,
                    percent_capital=request.percent_capital,
                    strategy_direction=request.strategy_direction,
                )

                point = HeatmapPoint(
                    take_profit=tp,
                    stop_loss=sl,
                    return_pct=result["return_pct"],
                    sharpe_ratio=result["sharpe_ratio"],
                    win_rate=result["win_rate"],
                    max_drawdown=result["max_drawdown"],
                    total_trades=result["total_trades"],
                )
                heatmap_data.append(point)

                # Track best result
                if result["return_pct"] > best_return:
                    best_return = result["return_pct"]
                    best_point = point

            except Exception as e:
                logger.error(f"Backtest failed for TP={tp}%, SL={sl}%: {e}")
                # Add empty point for failed backtest
                point = HeatmapPoint(
                    take_profit=tp,
                    stop_loss=sl,
                    return_pct=0.0,
                    sharpe_ratio=0.0,
                    win_rate=0.0,
                    max_drawdown=0.0,
                    total_trades=0,
                )
                heatmap_data.append(point)

    logger.info(f"Heatmap complete. Best: TP={best_point.take_profit}%, SL={best_point.stop_loss}% -> {best_return:.2f}%")

    return HeatmapResult(
        take_profit_values=take_profit_values,
        stop_loss_values=stop_loss_values,
        heatmap_data=heatmap_data,
        best_take_profit=best_point.take_profit if best_point else take_profit_values[0],
        best_stop_loss=best_point.stop_loss if best_point else stop_loss_values[0],
        best_return=best_return if best_return != float("-inf") else 0.0,
        total_backtests=total_backtests,
    )
