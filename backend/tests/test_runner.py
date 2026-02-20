"""Tests for backtest runner."""
from datetime import date

import pytest

from app.backtest.schemas import BacktestRequest, BacktestMetrics
from app.backtest.runner import calculate_metrics


def test_backtest_request_defaults():
    """Test BacktestRequest has correct defaults."""
    req = BacktestRequest(
        ticker="AAPL",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 30),
    )
    assert req.timeframe == "60min"
    assert req.stop_loss == 2.0
    assert req.take_profit == 4.0
    assert req.starting_capital == 10000.0


def test_calculate_metrics_no_trades():
    """Test metrics calculation with no trades."""
    metrics = calculate_metrics(
        initial_capital=10000,
        final_capital=10000,
        trades=[],
        equity_values=[10000],
    )
    assert metrics.total_return == 0.0
    assert metrics.total_trades == 0
    assert metrics.win_rate == 0.0


def test_calculate_metrics_with_trades():
    """Test metrics calculation with trades."""
    trades = [
        {"pnl": 100},
        {"pnl": 50},
        {"pnl": -30},
        {"pnl": 80},
    ]
    metrics = calculate_metrics(
        initial_capital=10000,
        final_capital=10200,
        trades=trades,
        equity_values=[10000, 10100, 10150, 10120, 10200],
    )
    assert metrics.total_return == 2.0
    assert metrics.total_trades == 4
    assert metrics.win_rate == 75.0
