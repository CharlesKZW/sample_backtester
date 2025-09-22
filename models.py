
from dataclasses import dataclass, field

class OrderError(Exception): pass
class ExecutionError(Exception): pass

class OrderStatus:
    NEW = "NEW"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"

@dataclass
class Order:
    symbol: str
    quantity: int
    price: float
    side: str
    status: str = field(default=OrderStatus.NEW)

    def validate(self):
        if self.side not in ("BUY","SELL"):
            raise OrderError(f"Invalid side: {self.side}")
        if not isinstance(self.quantity, int):
            raise OrderError("Quantity must be an integer.")
        if self.quantity <= 0:
            raise OrderError("Quantity must be positive.")
        if self.price <= 0:
            raise OrderError("Price must be positive.")
