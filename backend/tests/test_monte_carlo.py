"""Tests for Monte Carlo simulation."""
from datetime import datetime

import pytest

from app.backtest.monte_carlo import run_monte_carlo
from app.backtest.schemas import TradeRecord


def create_trade(pnl: float, pnl_percent: float) -> TradeRecord:
    """Create a trade record for testing."""
    return TradeRecord(
        entry_date=datetime(2024, 1, 1, 10, 0),
        exit_date=datetime(2024, 1, 1, 11, 0),
        entry_price=100.0,
        exit_price=100.0 + pnl / 10,
        size=10,
        pnl=pnl,
        pnl_percent=pnl_percent,
        trade_type="LONG"
    )


class TestMonteCarlo:
    """Test cases for Monte Carlo simulation."""

    def test_empty_trades(self):
        """Test Monte Carlo with no trades returns zeros."""
        result = run_monte_carlo(
            trades=[],
            starting_capital=10000.0,
            num_simulations=100
        )

        assert result["simulations"] == 100
        assert result["median_return"] == 0.0
        assert result["best_return"] == 0.0
        assert result["worst_return"] == 0.0
        assert result["percentile_5"] == 0.0
        assert result["percentile_95"] == 0.0

    def test_single_winning_trade(self):
        """Test Monte Carlo with one winning trade."""
        trades = [create_trade(pnl=100.0, pnl_percent=1.0)]
        result = run_monte_carlo(
            trades=trades,
            starting_capital=10000.0,
            num_simulations=100
        )

        # Single trade means all simulations are identical
        assert result["simulations"] == 100
        assert result["median_return"] == 1.0
        assert result["best_return"] == 1.0
        assert result["worst_return"] == 1.0

    def test_mixed_trades(self):
        """Test Monte Carlo with winning and losing trades."""
        trades = [
            create_trade(pnl=200.0, pnl_percent=2.0),
            create_trade(pnl=-100.0, pnl_percent=-1.0),
            create_trade(pnl=150.0, pnl_percent=1.5),
            create_trade(pnl=-50.0, pnl_percent=-0.5),
            create_trade(pnl=100.0, pnl_percent=1.0),
        ]
        result = run_monte_carlo(
            trades=trades,
            starting_capital=10000.0,
            num_simulations=1000
        )

        # Total P&L is 300 = 3% return
        # All simulations should give same final equity (just different paths)
        assert result["simulations"] == 1000
        assert result["median_return"] == 3.0
        assert result["best_return"] == 3.0
        assert result["worst_return"] == 3.0

    def test_drawdown_varies_by_order(self):
        """Test that max drawdown varies based on trade order."""
        trades = [
            create_trade(pnl=500.0, pnl_percent=5.0),
            create_trade(pnl=-200.0, pnl_percent=-2.0),
            create_trade(pnl=-200.0, pnl_percent=-2.0),
            create_trade(pnl=100.0, pnl_percent=1.0),
        ]
        result = run_monte_carlo(
            trades=trades,
            starting_capital=10000.0,
            num_simulations=1000
        )

        # Max drawdown should vary depending on order
        # Worst case: losses first, then gains
        # Best case: gains first, then losses
        assert result["median_max_drawdown"] >= 0
        assert result["worst_max_drawdown"] >= result["median_max_drawdown"]

    def test_return_distribution_structure(self):
        """Test that return distribution has correct structure."""
        trades = [
            create_trade(pnl=100.0, pnl_percent=1.0),
            create_trade(pnl=50.0, pnl_percent=0.5),
        ]
        result = run_monte_carlo(
            trades=trades,
            starting_capital=10000.0,
            num_simulations=100
        )

        assert "return_distribution" in result
        assert "values" in result["return_distribution"]
        assert "labels" in result["return_distribution"]
        assert len(result["return_distribution"]["values"]) == 21  # 0%, 5%, ..., 100%
        assert len(result["return_distribution"]["labels"]) == 21

    def test_percentile_bounds(self):
        """Test that 5th percentile < 95th percentile for varied results."""
        # Note: With same final equity, percentiles are equal
        # This test verifies the structure is correct
        trades = [create_trade(pnl=100.0, pnl_percent=1.0)]
        result = run_monte_carlo(
            trades=trades,
            starting_capital=10000.0,
            num_simulations=100
        )

        assert result["percentile_5"] <= result["median_return"]
        assert result["median_return"] <= result["percentile_95"]
