"""Paper trading simulation module."""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Type

import backtrader as bt
import pandas as pd

from app.backtest.schemas import (
    PaperTradePosition,
    PaperTradeResult,
    PaperTradeRequest,
    PaperTradeHistoryItem,
)
from app.data.alpha_vantage import AlphaVantageClient

logger = logging.getLogger(__name__)

# In-memory storage for paper trading sessions
# In production, this would be persisted to a database
paper_trading_sessions: Dict[str, PaperTradeResult] = {}


def get_recent_data(ticker: str, days: int = 30, interval: str = "60min") -> pd.DataFrame:
    """
    Fetch recent historical data for paper trading.

    Args:
        ticker: Stock ticker symbol
        days: Number of days of data to fetch
        interval: Candle interval

    Returns:
        DataFrame with OHLCV data
    """
    client = AlphaVantageClient()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    stock_data = client.get_intraday_data(
        ticker=ticker,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
    )

    if not stock_data.bars:
        raise ValueError(f"No data found for {ticker}")

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

    return df


def run_paper_trade_simulation(
    df: pd.DataFrame,
    strategy_class: Type[bt.Strategy],
    request: PaperTradeRequest,
) -> PaperTradeResult:
    """
    Run a paper trading simulation using recent historical data.

    This simulates what would have happened if you had traded
    with the strategy over the recent period.

    Args:
        df: DataFrame with OHLCV data
        strategy_class: Backtrader strategy class to use
        request: Paper trade request parameters

    Returns:
        PaperTradeResult with positions, P&L, and trade history
    """
    session_id = str(uuid.uuid4())
    logger.info(f"Starting paper trade session {session_id} for {request.ticker}")

    # Setup Backtrader
    cerebro = bt.Cerebro()

    # Add data feed
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)

    # Add strategy
    cerebro.addstrategy(
        strategy_class,
        stop_loss=request.stop_loss / 100,
        take_profit=request.take_profit / 100,
        risk_per_trade=request.risk_per_trade / 100,
        position_type=request.position_type,
        lot_size=request.lot_size,
        percent_capital=request.percent_capital / 100,
        strategy_direction=request.strategy_direction,
    )

    # Broker settings
    cerebro.broker.setcash(request.starting_capital)
    cerebro.broker.setcommission(commission=request.commission)
    cerebro.broker.set_slippage_perc(request.slippage / 100)

    # Run backtest (simulating paper trade)
    results = cerebro.run()
    strategy = results[0]

    # Get final state
    final_capital = cerebro.broker.getvalue()
    current_price = df["close"].iloc[-1]

    # Determine current position
    current_position: Optional[PaperTradePosition] = None
    if strategy.position:
        position_size = strategy.position.size
        entry_price = strategy.entry_price if strategy.entry_price else current_price

        if position_size != 0:
            direction = "LONG" if position_size > 0 else "SHORT"
            if direction == "LONG":
                unrealized_pnl = (current_price - entry_price) * abs(position_size)
                unrealized_pnl_pct = ((current_price - entry_price) / entry_price) * 100
            else:
                unrealized_pnl = (entry_price - current_price) * abs(position_size)
                unrealized_pnl_pct = ((entry_price - current_price) / entry_price) * 100

            current_position = PaperTradePosition(
                ticker=request.ticker,
                direction=direction,
                size=abs(position_size),
                entry_price=entry_price,
                current_price=current_price,
                unrealized_pnl=round(unrealized_pnl, 2),
                unrealized_pnl_pct=round(unrealized_pnl_pct, 2),
                entry_date=df.index[-1],  # Approximate
            )

    # Convert trade history
    trade_history = []
    for trade in strategy.trades:
        trade_history.append(PaperTradeHistoryItem(
            entry_date=trade["entry_date"],
            exit_date=trade["exit_date"],
            direction=trade.get("trade_type", "LONG"),
            size=trade["size"],
            entry_price=trade["entry_price"],
            exit_price=trade["exit_price"],
            pnl=round(trade["pnl"], 2),
            pnl_pct=round(trade["pnl_percent"], 2),
        ))

    # Calculate realized P&L
    realized_pnl = sum(t["pnl"] for t in strategy.trades)
    realized_pnl_pct = ((final_capital - request.starting_capital) / request.starting_capital) * 100

    # Calculate total P&L (realized + unrealized)
    unrealized = current_position.unrealized_pnl if current_position else 0.0
    total_pnl = realized_pnl + unrealized

    result = PaperTradeResult(
        session_id=session_id,
        ticker=request.ticker,
        strategy_name=request.strategy_name,
        start_date=df.index[0],
        end_date=df.index[-1],
        starting_capital=request.starting_capital,
        current_capital=round(final_capital, 2),
        current_position=current_position,
        realized_pnl=round(realized_pnl, 2),
        realized_pnl_pct=round(realized_pnl_pct, 2),
        unrealized_pnl=round(unrealized, 2),
        total_pnl=round(total_pnl, 2),
        total_trades=len(strategy.trades),
        trade_history=trade_history,
        is_active=True,
        last_updated=datetime.now(),
    )

    # Store session
    paper_trading_sessions[session_id] = result

    logger.info(f"Paper trade session {session_id} complete: {len(strategy.trades)} trades, ${total_pnl:.2f} P&L")

    return result


def get_paper_trade_status(session_id: str) -> Optional[PaperTradeResult]:
    """
    Get the status of an active paper trading session.

    Args:
        session_id: The session ID to look up

    Returns:
        PaperTradeResult if found, None otherwise
    """
    return paper_trading_sessions.get(session_id)


def list_paper_trade_sessions() -> list[PaperTradeResult]:
    """
    List all paper trading sessions.

    Returns:
        List of all paper trade sessions
    """
    return list(paper_trading_sessions.values())


def stop_paper_trade(session_id: str) -> Optional[PaperTradeResult]:
    """
    Stop a paper trading session.

    Args:
        session_id: The session ID to stop

    Returns:
        Final PaperTradeResult if found, None otherwise
    """
    if session_id in paper_trading_sessions:
        result = paper_trading_sessions[session_id]
        result.is_active = False
        result.last_updated = datetime.now()
        return result
    return None
