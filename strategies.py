
"""
Strategy interfaces and concrete strategies.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple
from collections import deque
import statistics

from data_loader import MarketDataPoint

Signal = Tuple[str, str, int, float]  # (action, symbol, qty, price)

class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> List[Signal]:
        """Return a list of signals (action, symbol, qty, price) for the tick."""
        raise NotImplementedError

class MomentumStrategy(Strategy):
    """
    Simple momentum: compare current price vs price N ticks ago, trade if difference
    exceeds a threshold.
    """
    def __init__(self, symbol: str, lookback: int = 3, qty: int = 1, threshold: float = 0.0):
        self.symbol = symbol
        self._lookback = lookback
        self._qty = qty
        self._threshold = threshold
        self._prices = deque(maxlen=lookback + 1)

    def generate_signals(self, tick: MarketDataPoint) -> List[Signal]:
        sigs: List[Signal] = []
        if tick.symbol != self.symbol:
            return sigs

        self._prices.append(tick.price)
        if len(self._prices) > self._lookback:
            past = self._prices[0]
            diff = tick.price - past
            if diff > self._threshold:
                sigs.append(("BUY", tick.symbol, self._qty, tick.price))
            elif diff < -self._threshold:
                sigs.append(("SELL", tick.symbol, self._qty, tick.price))
        return sigs

class MeanReversionStrategy(Strategy):
    """
    Mean reversion using rolling z-score: buy when price is 1 std below mean,
    sell when 1 std above.
    """
    def __init__(self, symbol: str, window: int = 20, z_entry: float = 1.0, qty: int = 1):
        self.symbol = symbol
        self._window = window
        self._z_entry = z_entry
        self._qty = qty
        self._prices = deque(maxlen=window)

    def _z(self, value: float, series) -> float:
        if len(series) < 2:
            return 0.0
        mu = statistics.fmean(series)
        try:
            sigma = statistics.pstdev(series)
        except statistics.StatisticsError:
            sigma = 0.0
        return 0.0 if sigma == 0 else (value - mu) / sigma

    def generate_signals(self, tick: MarketDataPoint) -> List[Signal]:
        sigs: List[Signal] = []
        if tick.symbol != self.symbol:
            return sigs

        self._prices.append(tick.price)
        if len(self._prices) == self._window:
            z = self._z(tick.price, self._prices)
            if z > self._z_entry:
                sigs.append(("SELL", tick.symbol, self._qty, tick.price))
            elif z < -self._z_entry:
                sigs.append(("BUY", tick.symbol, self._qty, tick.price))
        return sigs
