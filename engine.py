
from typing import Dict, List, Tuple
import random, datetime
from models import Order, OrderError, ExecutionError, OrderStatus
from data_loader import MarketDataPoint

class ExecutionEngine:
    def __init__(self, starting_cash: float = 100_000.0, success_rate: float = 0.9):
        self.positions: Dict[str, Dict[str, float]] = {}
        self.cash: float = starting_cash
        self.executed_history: List[Dict] = []
        self.failed_history: List[Dict] = []
        self.portfolio_values: List[Tuple[datetime.datetime, float]] = []
        self._last_prices: Dict[str, float] = {}
        self.success_rate = success_rate
    def _get_pos(self, symbol: str) -> Dict[str, float]:
        return self.positions.setdefault(symbol, {"quantity": 0, "avg_price": 0.0})
    def _mark_price(self, symbol: str, price: float):
        self._last_prices[symbol] = price
    def _portfolio_value(self) -> float:
        value = self.cash
        for sym, pos in self.positions.items():
            qty = pos["quantity"]
            px = self._last_prices.get(sym, pos["avg_price"])
            value += qty * px
        return value
    def execute(self, order: Order, now: datetime.datetime):
        order.validate()
        pos = self._get_pos(order.symbol)
        if order.side == "SELL" and order.quantity > pos["quantity"]:
            raise OrderError(f"Cannot sell {order.quantity} > current position {pos['quantity']} for {order.symbol}")
        if random.random() < self.success_rate:
            order.status = OrderStatus.FILLED
            if order.side == "BUY":
                total_cost = pos["avg_price"] * pos["quantity"] + order.price * order.quantity
                new_qty = pos["quantity"] + order.quantity
                pos["quantity"] = new_qty
                pos["avg_price"] = total_cost / new_qty if new_qty > 0 else 0.0
                self.cash -= order.price * order.quantity
            else:
                pos["quantity"] -= order.quantity
                self.cash += order.price * order.quantity
                if pos["quantity"] == 0: pos["avg_price"] = 0.0
            self.executed_history.append({
                "timestamp": now.isoformat(),
                "symbol": order.symbol,
                "price": order.price,
                "quantity": order.quantity,
                "side": order.side,
                "status": order.status,
                "cash_after": self.cash,
                "position_after": pos["quantity"],
            })
        else:
            order.status = OrderStatus.FAILED
            self.failed_history.append({
                "timestamp": now.isoformat(),
                "symbol": order.symbol,
                "price": order.price,
                "quantity": order.quantity,
                "side": order.side,
                "status": order.status,
                "reason": "Simulated failure"
            })
            raise ExecutionError(f"Execution failed for {order.side} {order.quantity} {order.symbol} @ {order.price}")
    def on_tick(self, tick: MarketDataPoint):
        self._mark_price(tick.symbol, tick.price)
        self.portfolio_values.append((tick.timestamp, self._portfolio_value()))
