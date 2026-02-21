"""Monte Carlo simulation for backtest robustness testing."""
import logging
import random
from typing import List

import numpy as np

from app.backtest.schemas import TradeRecord

logger = logging.getLogger(__name__)


def run_monte_carlo(
    trades: List[TradeRecord],
    starting_capital: float,
    num_simulations: int = 1000
) -> dict:
    """
    Run Monte Carlo simulation by shuffling trade order.

    This tests strategy robustness by randomizing the order of trades
    and calculating the distribution of possible outcomes.

    Args:
        trades: List of completed trades from backtest
        starting_capital: Initial capital amount
        num_simulations: Number of random shuffles to run (default 1000)

    Returns:
        Dictionary with simulation statistics and distribution data
    """
    logger.info(f"Running Monte Carlo simulation with {num_simulations} iterations")

    if not trades:
        logger.warning("No trades provided for Monte Carlo simulation")
        return {
            "simulations": num_simulations,
            "median_return": 0.0,
            "best_return": 0.0,
            "worst_return": 0.0,
            "percentile_5": 0.0,
            "percentile_95": 0.0,
            "median_max_drawdown": 0.0,
            "worst_max_drawdown": 0.0,
            "return_distribution": {
                "values": [],
                "labels": []
            }
        }

    # Extract P&L from each trade
    pnls = [t.pnl for t in trades]
    logger.info(f"Simulating {len(pnls)} trades across {num_simulations} scenarios")

    final_equities = []
    max_drawdowns = []

    for i in range(num_simulations):
        # Shuffle trade order
        shuffled_pnls = pnls.copy()
        random.shuffle(shuffled_pnls)

        # Calculate equity curve
        equity = starting_capital
        peak = equity
        max_dd = 0.0

        for pnl in shuffled_pnls:
            equity += pnl
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak * 100 if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd

        final_equities.append(equity)
        max_drawdowns.append(max_dd)

    # Calculate statistics
    final_equities = np.array(final_equities)
    max_drawdowns = np.array(max_drawdowns)

    returns = ((final_equities - starting_capital) / starting_capital) * 100

    # Calculate percentiles for histogram
    percentile_values = [float(np.percentile(returns, i)) for i in range(0, 101, 5)]
    percentile_labels = [f"{i}%" for i in range(0, 101, 5)]

    result = {
        "simulations": num_simulations,
        "median_return": round(float(np.median(returns)), 2),
        "best_return": round(float(np.max(returns)), 2),
        "worst_return": round(float(np.min(returns)), 2),
        "percentile_5": round(float(np.percentile(returns, 5)), 2),
        "percentile_95": round(float(np.percentile(returns, 95)), 2),
        "median_max_drawdown": round(float(np.median(max_drawdowns)), 2),
        "worst_max_drawdown": round(float(np.max(max_drawdowns)), 2),
        "return_distribution": {
            "values": [round(v, 2) for v in percentile_values],
            "labels": percentile_labels
        }
    }

    logger.info(
        f"Monte Carlo complete: median return {result['median_return']}%, "
        f"range [{result['worst_return']}%, {result['best_return']}%]"
    )

    return result
