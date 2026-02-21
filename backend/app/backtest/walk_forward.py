"""Walk-Forward Testing module.

Walk-forward analysis tests strategy robustness by:
1. Splitting data into multiple rolling windows
2. For each window: train on first portion, test on remaining
3. Measuring performance consistency across all windows

This helps detect overfitting - a strategy that only works on specific data.
"""
import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def run_walk_forward(
    df: pd.DataFrame,
    strategy_func: Optional[callable] = None,
    strategy_params: Optional[dict] = None,
    num_windows: int = 5,
    train_pct: float = 0.8,
) -> dict:
    """
    Run walk-forward analysis with rolling windows.

    Args:
        df: DataFrame with OHLCV data, datetime index
        strategy_func: Strategy function to run (optional for MVP)
        strategy_params: Strategy parameters dict
        num_windows: Number of rolling windows to test
        train_pct: Percentage of each window used for training (0.8 = 80%)

    Returns:
        Dictionary with walk-forward results:
        - num_windows: Number of completed windows
        - windows: List of window results
        - overall_consistency: Percentage of profitable windows
        - avg_return: Average return across windows
        - profitable_windows: Count of profitable windows
    """
    logger.info(f"Starting walk-forward analysis with {num_windows} windows")

    # Validate input
    if df is None or df.empty:
        logger.warning("Empty dataframe provided to walk-forward")
        return _empty_result(num_windows)

    min_rows_per_window = 10
    if len(df) < num_windows * min_rows_per_window:
        logger.warning(
            f"Insufficient data for walk-forward: {len(df)} rows, "
            f"need at least {num_windows * min_rows_per_window}"
        )
        return _empty_result(num_windows)

    # Calculate window size
    total_rows = len(df)
    window_size = total_rows // num_windows

    logger.info(f"Total rows: {total_rows}, window size: {window_size}")

    windows_results = []
    profitable_count = 0
    total_return = 0.0

    for i in range(num_windows):
        # Calculate window boundaries
        start_idx = i * window_size
        end_idx = start_idx + window_size if i < num_windows - 1 else total_rows

        window_df = df.iloc[start_idx:end_idx].copy()

        # Split into train/test
        train_size = int(len(window_df) * train_pct)
        test_size = len(window_df) - train_size

        if test_size < 5:
            logger.warning(f"Window {i+1}: test portion too small ({test_size} rows)")
            continue

        test_df = window_df.iloc[train_size:]

        # Get date range for this window
        start_date = _format_date(window_df.index[0])
        end_date = _format_date(window_df.index[-1])
        train_end_date = _format_date(window_df.index[train_size - 1])
        test_start_date = _format_date(test_df.index[0])

        # Calculate return on test portion
        # For MVP: use simple price change as proxy for strategy return
        # A full implementation would run the actual strategy here
        if "close" in test_df.columns:
            close_col = "close"
        elif "Close" in test_df.columns:
            close_col = "Close"
        else:
            logger.error(f"Window {i+1}: no close column found")
            continue

        first_close = test_df[close_col].iloc[0]
        last_close = test_df[close_col].iloc[-1]

        if first_close <= 0:
            logger.warning(f"Window {i+1}: invalid first close price")
            continue

        window_return = ((last_close - first_close) / first_close) * 100

        is_profitable = window_return > 0
        if is_profitable:
            profitable_count += 1

        total_return += window_return

        window_result = {
            "window": i + 1,
            "start_date": start_date,
            "end_date": end_date,
            "train_end_date": train_end_date,
            "test_start_date": test_start_date,
            "train_size": train_size,
            "test_size": test_size,
            "return_pct": round(window_return, 2),
            "profitable": is_profitable,
        }

        windows_results.append(window_result)
        logger.info(
            f"Window {i+1}: {start_date} to {end_date}, "
            f"return: {window_return:.2f}%, profitable: {is_profitable}"
        )

    # Calculate overall metrics
    num_completed = len(windows_results)
    consistency = (profitable_count / num_completed * 100) if num_completed > 0 else 0.0
    avg_return = (total_return / num_completed) if num_completed > 0 else 0.0

    result = {
        "num_windows": num_completed,
        "windows": windows_results,
        "overall_consistency": round(consistency, 1),
        "avg_return": round(avg_return, 2),
        "profitable_windows": profitable_count,
        "train_pct": train_pct,
    }

    logger.info(
        f"Walk-forward complete: {num_completed} windows, "
        f"{profitable_count} profitable ({consistency:.1f}%), "
        f"avg return: {avg_return:.2f}%"
    )

    return result


def _format_date(dt) -> str:
    """Format datetime to date string."""
    if hasattr(dt, "strftime"):
        return dt.strftime("%Y-%m-%d")
    return str(dt)[:10]


def _empty_result(num_windows: int) -> dict:
    """Return empty result structure."""
    return {
        "num_windows": 0,
        "windows": [],
        "overall_consistency": 0.0,
        "avg_return": 0.0,
        "profitable_windows": 0,
        "train_pct": 0.8,
    }
