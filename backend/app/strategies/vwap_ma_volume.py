"""VWAP + MA200 + Volume strategy."""
import backtrader as bt

from app.strategies.indicators import VWAP


class VWAPMAVolumeStrategy(bt.Strategy):
    """
    VWAP + MA200 + Volume Strategy.

    Entry conditions (BUY):
    - Price above VWAP
    - Price above MA200
    - Volume above average (volume spike)

    Exit conditions:
    - Stop loss hit
    - Take profit hit
    """

    params = (
        ("vwap_period", 14),
        ("ma_period", 200),
        ("volume_period", 20),
        ("volume_mult", 1.5),
        ("stop_loss", 0.02),
        ("take_profit", 0.04),
        ("risk_per_trade", 0.02),
        ("position_type", "percent"),  # "fixed" or "percent"
        ("lot_size", 50),
        ("percent_capital", 0.10),
    )

    def __init__(self):
        self.vwap = VWAP(self.data, period=self.p.vwap_period)
        self.ma200 = bt.ind.SMA(self.data.close, period=self.p.ma_period)
        self.volume_avg = bt.ind.SMA(self.data.volume, period=self.p.volume_period)

        self.order = None
        self.entry_price = None
        self.trades = []

    def log(self, txt):
        """Log message with datetime."""
        dt = self.data.datetime.datetime(0)
        print(f"{dt.isoformat()} - {txt}")

    def notify_order(self, order):
        """Handle order notifications."""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.entry_price = order.executed.price
                self.log(f"BUY EXECUTED @ {order.executed.price:.2f}")
            else:
                self.log(f"SELL EXECUTED @ {order.executed.price:.2f}")

        self.order = None

    def notify_trade(self, trade):
        """Handle trade notifications."""
        if trade.isclosed:
            self.trades.append({
                "entry_date": bt.num2date(trade.dtopen),
                "exit_date": bt.num2date(trade.dtclose),
                "entry_price": trade.price,
                "exit_price": trade.price + trade.pnl / trade.size,
                "size": trade.size,
                "pnl": trade.pnl,
                "pnl_percent": (trade.pnl / (trade.price * abs(trade.size))) * 100,
            })

    def next(self):
        """Execute strategy logic on each bar."""
        if self.order:
            return

        if not self.position:
            # Entry conditions
            price_above_vwap = self.data.close[0] > self.vwap[0]
            price_above_ma = self.data.close[0] > self.ma200[0]
            volume_spike = self.data.volume[0] > self.volume_avg[0] * self.p.volume_mult

            if price_above_vwap and price_above_ma and volume_spike:
                # Calculate position size
                if self.p.position_type == "fixed":
                    size = self.p.lot_size
                else:
                    value = self.broker.getvalue() * self.p.percent_capital
                    size = int(value / self.data.close[0])

                if size > 0:
                    self.order = self.buy(size=size)
        else:
            # Exit conditions
            pnl_pct = (self.data.close[0] - self.entry_price) / self.entry_price

            if pnl_pct <= -self.p.stop_loss:
                self.log(f"STOP LOSS HIT @ {pnl_pct*100:.2f}%")
                self.order = self.sell(size=self.position.size)
            elif pnl_pct >= self.p.take_profit:
                self.log(f"TAKE PROFIT HIT @ {pnl_pct*100:.2f}%")
                self.order = self.sell(size=self.position.size)
