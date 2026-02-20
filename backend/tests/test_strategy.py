"""Tests for trading strategy."""
from datetime import datetime

import backtrader as bt
import pytest

from app.strategies.vwap_ma_volume import VWAPMAVolumeStrategy


class MockData(bt.feeds.PandasData):
    """Mock data feed for testing."""
    pass


def test_strategy_initializes():
    """Test strategy can be instantiated."""
    cerebro = bt.Cerebro()
    cerebro.addstrategy(VWAPMAVolumeStrategy)

    # Verify strategy is added
    assert len(cerebro.strats) == 1


def test_strategy_params():
    """Test strategy has correct default params."""
    strategy_cls = VWAPMAVolumeStrategy
    assert strategy_cls.params.stop_loss == 0.02
    assert strategy_cls.params.take_profit == 0.04
    assert strategy_cls.params.ma_period == 200
