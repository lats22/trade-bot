"""Backtest runner module."""
from app.backtest.runner import run_backtest, get_strategy_class, STRATEGY_REGISTRY
from app.backtest.monte_carlo import run_monte_carlo
from app.backtest.walk_forward import run_walk_forward
from app.backtest.parameter_heatmap import run_parameter_heatmap
from app.backtest.paper_trading import (
    run_paper_trade_simulation,
    get_paper_trade_status,
    list_paper_trade_sessions,
    stop_paper_trade,
)

__all__ = [
    "run_backtest",
    "get_strategy_class",
    "STRATEGY_REGISTRY",
    "run_monte_carlo",
    "run_walk_forward",
    "run_parameter_heatmap",
    "run_paper_trade_simulation",
    "get_paper_trade_status",
    "list_paper_trade_sessions",
    "stop_paper_trade",
]
