"""VWAP + MA200 + Volume strategy."""
import logging

import backtrader as bt

from app.strategies.indicators import VWAP

logger = logging.getLogger(__name__)


class VWAPMAVolumeStrategy(bt.Strategy):
    """
    VWAP + MA200 + Volume Strategy.

    Entry conditions (LONG):
    - Price above VWAP
    - Price above MA200
    - Volume above average (volume spike)

    Entry conditions (SHORT):
    - Price below VWAP
    - Price below MA200
    - Volume above average (volume spike)

    Exit conditions:
    - Stop loss hit
    - Take profit hit
    """

    params = (
        ("vwap_period", 14),
        ("ma_period", 20),  # Reduced from 200 for limited data
        ("volume_period", 10),  # Reduced from 20 for limited data
        ("volume_mult", 1.5),
        ("stop_loss", 0.02),
        ("take_profit", 0.04),
        ("risk_per_trade", 0.02),
        ("position_type", "percent"),  # "fixed" or "percent"
        ("lot_size", 50),
        ("percent_capital", 0.10),
        ("strategy_direction", "long"),  # "long", "short", or "both"
    )

    def __init__(self):
        self.vwap = VWAP(self.data, period=self.p.vwap_period)
        self.ma200 = bt.ind.SMA(self.data.close, period=self.p.ma_period)
        self.volume_avg = bt.ind.SMA(self.data.volume, period=self.p.volume_period)

        self.order = None
        self.entry_price = None
        self.position_direction = None  # Track if current position is "long" or "short"
        self.trades = []

    def log(self, txt):
        """Log message with datetime."""
        dt = self.data.datetime.datetime(0)
        logger.info(f"{dt.isoformat()} - {txt}")

    def notify_order(self, order):
        """Handle order notifications."""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                if self.position_direction == "short":
                    # Covering a short position
                    self.log(f"SHORT COVER EXECUTED @ {order.executed.price:.2f}")
                else:
                    # Opening a long position
                    self.entry_price = order.executed.price
                    self.position_direction = "long"
                    self.log(f"LONG ENTRY EXECUTED @ {order.executed.price:.2f}")
            else:
                if self.position_direction == "long":
                    # Closing a long position
                    self.log(f"LONG EXIT EXECUTED @ {order.executed.price:.2f}")
                else:
                    # Opening a short position
                    self.entry_price = order.executed.price
                    self.position_direction = "short"
                    self.log(f"SHORT ENTRY EXECUTED @ {order.executed.price:.2f}")

        self.order = None

    def notify_trade(self, trade):
        """Handle trade notifications."""
        if trade.isclosed:
            size = abs(trade.size) if trade.size != 0 else 1
            entry_value = trade.price * size if trade.price and size else 1
            # Determine trade type from position direction
            trade_type = self.position_direction if self.position_direction else "long"
            self.trades.append({
                "entry_date": bt.num2date(trade.dtopen),
                "exit_date": bt.num2date(trade.dtclose),
                "entry_price": trade.price,
                "exit_price": trade.price + (trade.pnl / size) if size else trade.price,
                "size": size,
                "pnl": trade.pnl,
                "pnl_percent": (trade.pnl / entry_value) * 100 if entry_value else 0,
                "trade_type": trade_type.upper(),
            })
            # Reset position direction after trade closes
            self.position_direction = None

    def _calculate_position_size(self):
        """Calculate position size based on settings."""
        if self.p.position_type == "fixed":
            return self.p.lot_size
        else:
            value = self.broker.getvalue() * self.p.percent_capital
            return int(value / self.data.close[0])

    def next(self):
        """Execute strategy logic on each bar."""
        if self.order:
            return

        # Calculate common conditions
        price_above_vwap = self.data.close[0] > self.vwap[0]
        price_above_ma = self.data.close[0] > self.ma200[0]
        price_below_vwap = self.data.close[0] < self.vwap[0]
        price_below_ma = self.data.close[0] < self.ma200[0]
        volume_spike = self.data.volume[0] > self.volume_avg[0] * self.p.volume_mult

        if not self.position:
            # No position - check for entry signals
            size = self._calculate_position_size()
            if size <= 0:
                return

            # Long entry conditions
            long_signal = price_above_vwap and price_above_ma and volume_spike
            # Short entry conditions (opposite of long)
            short_signal = price_below_vwap and price_below_ma and volume_spike

            direction = self.p.strategy_direction

            if direction == "long" and long_signal:
                self.log("LONG SIGNAL - Opening long position")
                self.order = self.buy(size=size)
            elif direction == "short" and short_signal:
                self.log("SHORT SIGNAL - Opening short position")
                self.order = self.sell(size=size)
            elif direction == "both":
                # In "both" mode, prefer the current signal
                if long_signal:
                    self.log("LONG SIGNAL (both mode) - Opening long position")
                    self.order = self.buy(size=size)
                elif short_signal:
                    self.log("SHORT SIGNAL (both mode) - Opening short position")
                    self.order = self.sell(size=size)
        else:
            # Have a position - check for exit conditions
            if self.position_direction == "long":
                # Long position exit logic
                pnl_pct = (self.data.close[0] - self.entry_price) / self.entry_price

                if pnl_pct <= -self.p.stop_loss:
                    self.log(f"LONG STOP LOSS HIT @ {pnl_pct*100:.2f}%")
                    self.order = self.sell(size=self.position.size)
                elif pnl_pct >= self.p.take_profit:
                    self.log(f"LONG TAKE PROFIT HIT @ {pnl_pct*100:.2f}%")
                    self.order = self.sell(size=self.position.size)

            elif self.position_direction == "short":
                # Short position exit logic (reversed)
                # For shorts: profit when price goes down, loss when price goes up
                pnl_pct = (self.entry_price - self.data.close[0]) / self.entry_price

                if pnl_pct <= -self.p.stop_loss:
                    # Price went up - stop loss hit
                    self.log(f"SHORT STOP LOSS HIT @ {pnl_pct*100:.2f}%")
                    self.order = self.buy(size=abs(self.position.size))
                elif pnl_pct >= self.p.take_profit:
                    # Price went down - take profit hit
                    self.log(f"SHORT TAKE PROFIT HIT @ {pnl_pct*100:.2f}%")
                    self.order = self.buy(size=abs(self.position.size))
