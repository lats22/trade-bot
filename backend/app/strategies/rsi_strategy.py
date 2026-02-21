"""RSI Overbought/Oversold strategy."""
import logging

import backtrader as bt

logger = logging.getLogger(__name__)


class RSIStrategy(bt.Strategy):
    """
    RSI Overbought/Oversold Strategy.

    Entry conditions (LONG):
    - RSI crosses above oversold level (default 30)

    Entry conditions (SHORT):
    - RSI crosses below overbought level (default 70)

    Exit conditions:
    - Stop loss hit
    - Take profit hit
    - RSI reaches opposite extreme
    """

    params = (
        ("rsi_period", 14),
        ("oversold", 30),
        ("overbought", 70),
        ("stop_loss", 0.02),
        ("take_profit", 0.04),
        ("risk_per_trade", 0.02),
        ("position_type", "percent"),  # "fixed" or "percent"
        ("lot_size", 50),
        ("percent_capital", 0.10),
        ("strategy_direction", "long"),  # "long", "short", or "both"
    )

    def __init__(self):
        self.rsi = bt.ind.RSI(self.data.close, period=self.p.rsi_period)

        self.order = None
        self.entry_price = None
        self.position_direction = None
        self.trades = []

        # Track previous RSI for crossover detection
        self.prev_rsi = None

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
                    self.log(f"SHORT COVER EXECUTED @ {order.executed.price:.2f}")
                else:
                    self.entry_price = order.executed.price
                    self.position_direction = "long"
                    self.log(f"LONG ENTRY EXECUTED @ {order.executed.price:.2f}")
            else:
                if self.position_direction == "long":
                    self.log(f"LONG EXIT EXECUTED @ {order.executed.price:.2f}")
                else:
                    self.entry_price = order.executed.price
                    self.position_direction = "short"
                    self.log(f"SHORT ENTRY EXECUTED @ {order.executed.price:.2f}")

        self.order = None

    def notify_trade(self, trade):
        """Handle trade notifications."""
        if trade.isclosed:
            size = abs(trade.size) if trade.size != 0 else 1
            entry_value = trade.price * size if trade.price and size else 1
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

        current_rsi = self.rsi[0]

        # Initialize prev_rsi on first bar
        if self.prev_rsi is None:
            self.prev_rsi = current_rsi
            return

        direction = self.p.strategy_direction

        if not self.position:
            size = self._calculate_position_size()
            if size <= 0:
                self.prev_rsi = current_rsi
                return

            # RSI crosses above oversold = long signal
            long_signal = self.prev_rsi <= self.p.oversold and current_rsi > self.p.oversold
            # RSI crosses below overbought = short signal
            short_signal = self.prev_rsi >= self.p.overbought and current_rsi < self.p.overbought

            if direction == "long" and long_signal:
                self.log(f"RSI OVERSOLD BOUNCE ({current_rsi:.1f}) - Opening long position")
                self.order = self.buy(size=size)
            elif direction == "short" and short_signal:
                self.log(f"RSI OVERBOUGHT DROP ({current_rsi:.1f}) - Opening short position")
                self.order = self.sell(size=size)
            elif direction == "both":
                if long_signal:
                    self.log(f"RSI OVERSOLD BOUNCE ({current_rsi:.1f}) - Opening long position")
                    self.order = self.buy(size=size)
                elif short_signal:
                    self.log(f"RSI OVERBOUGHT DROP ({current_rsi:.1f}) - Opening short position")
                    self.order = self.sell(size=size)
        else:
            # Check for exit conditions
            if self.position_direction == "long":
                pnl_pct = (self.data.close[0] - self.entry_price) / self.entry_price

                if pnl_pct <= -self.p.stop_loss:
                    self.log(f"LONG STOP LOSS HIT @ {pnl_pct*100:.2f}%")
                    self.order = self.sell(size=self.position.size)
                elif pnl_pct >= self.p.take_profit:
                    self.log(f"LONG TAKE PROFIT HIT @ {pnl_pct*100:.2f}%")
                    self.order = self.sell(size=self.position.size)
                elif current_rsi >= self.p.overbought:
                    self.log(f"RSI OVERBOUGHT ({current_rsi:.1f}) - Closing long position")
                    self.order = self.sell(size=self.position.size)

            elif self.position_direction == "short":
                pnl_pct = (self.entry_price - self.data.close[0]) / self.entry_price

                if pnl_pct <= -self.p.stop_loss:
                    self.log(f"SHORT STOP LOSS HIT @ {pnl_pct*100:.2f}%")
                    self.order = self.buy(size=abs(self.position.size))
                elif pnl_pct >= self.p.take_profit:
                    self.log(f"SHORT TAKE PROFIT HIT @ {pnl_pct*100:.2f}%")
                    self.order = self.buy(size=abs(self.position.size))
                elif current_rsi <= self.p.oversold:
                    self.log(f"RSI OVERSOLD ({current_rsi:.1f}) - Closing short position")
                    self.order = self.buy(size=abs(self.position.size))

        self.prev_rsi = current_rsi
