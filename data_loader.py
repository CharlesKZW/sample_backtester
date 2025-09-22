
"""
Data loading utilities and the immutable MarketDataPoint type.
"""
from dataclasses import dataclass
from typing import List
import csv
import datetime

@dataclass(frozen=True)
class MarketDataPoint:
    """
    Immutable tick record parsed from CSV.
    """
    timestamp: datetime.datetime
    symbol: str
    price: float

def load_market_data(csv_path: str) -> List[MarketDataPoint]:
    """
    Read CSV with columns: timestamp, symbol, price and return ordered list of MarketDataPoint.
    Timestamps must be ISO8601 strings (e.g., '2025-09-21T12:34:56.789123').
    """
    records: List[MarketDataPoint] = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = datetime.datetime.fromisoformat(row["timestamp"])
            sym = row["symbol"]
            px = float(row["price"])
            records.append(MarketDataPoint(ts, sym, px))
    # Ensure chronological order
    records.sort(key=lambda r: r.timestamp)
    return records
