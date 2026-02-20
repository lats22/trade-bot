"""Custom Backtrader indicators."""
import backtrader as bt


class VWAP(bt.Indicator):
    """Volume Weighted Average Price indicator."""

    lines = ("vwap",)
    params = (("period", 14),)

    def __init__(self):
        cumvol = bt.ind.SumN(self.data.volume, period=self.p.period)
        cumtp = bt.ind.SumN(
            self.data.close * self.data.volume, period=self.p.period
        )
        self.lines.vwap = cumtp / cumvol
