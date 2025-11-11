"""
Defines the core data models for the matching engine.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class Side(Enum):
    """Enumeration for the two sides of an order."""
    BUY = "Buy"
    SELL = "Sell"

@dataclass
class Order:
    """
    Represents a single order in the system.

    The `Quantity` field is mutable, as it will be modified
    (decremented) by the matching engine as it's filled.
    """
    OrderID: str
    CreateTime: datetime
    Side: Side
    Price: float
    Quantity: int

@dataclass
class Execution:
    """
    Represents a single trade execution (a fill).
    
    This object is created and returned when a match occurs.
    """
    ExecutionID: int
    Price: float
    Quantity: int
    Sell_OrderID: str
    Buy_OrderID: str