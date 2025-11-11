"""
Defines the abstract OrderBook and its concrete implementations.

This module encapsulates the heap-based data structure and
priority-sorting logic for both buy and sell sides.
"""

import heapq
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Tuple

from .models import Order

# Type alias for our heap entries.
# We store (priority, time, order_object)
HeapEntry = Tuple[float, datetime, Order]

class OrderBook(ABC):
    """
    Abstract base class for an order book.
    
    It provides a common interface for adding, removing,
    and matching orders, but the priority logic is
    defined in its subclasses.
    """
    
    def __init__(self):
        # self._book is our min-heap
        self._book: List[HeapEntry] = []

    def add(self, order: Order):
        """Adds a new order to the book."""
        entry = self._create_heap_entry(order)
        heapq.heappush(self._book, entry)

    def peek(self) -> Optional[Order]:
        """Returns the best-priority order without removing it."""
        if not self.is_empty():
            return self._book[0][2] # (priority, time, order) -> order
        return None

    def pop(self) -> Optional[Order]:
        """Removes and returns the best-priority order."""
        if not self.is_empty():
            return heapq.heappop(self._book)[2] # (priority, time, order) -> order
        return None

    def is_empty(self) -> bool:
        """Checks if the order book is empty."""
        return not self._book

    @abstractmethod
    def _create_heap_entry(self, order: Order) -> HeapEntry:
        """
        Abstract method for creating a heap-sortable entry.
        This defines the priority logic.
        """
        pass

    @abstractmethod
    def can_match(self, price: float) -> bool:
        """
        Checks if the best order in the book can be matched
        against an incoming order's price.
        """
        pass


class BuyBook(OrderBook):
    """
    Implementation of an OrderBook for BUY orders.
    
    Priority is given to the HIGHEST price.
    We achieve this by storing the *negative* price in our min-heap.
    """
    
    def _create_heap_entry(self, order: Order) -> HeapEntry:
        """
        Creates a heap entry for a buy order.
        Priority is -Price (to create a max-heap).
        Tie-breaker is CreateTime.
        """
        return (-order.Price, order.CreateTime, order)

    def can_match(self, sell_price: float) -> bool:
        """
        Checks if the best buy order (highest price) is
        greater than or equal to the incoming sell price.
        """
        best_buy = self.peek()
        return (best_buy is not None) and (best_buy.Price >= sell_price)


class SellBook(OrderBook):
    """
    Implementation of an OrderBook for SELL orders.
    
    Priority is given to the LOWEST price.
    We achieve this by storing the price directly in our min-heap.
    """
    
    def _create_heap_entry(self, order: Order) -> HeapEntry:
        """
        Creates a heap entry for a sell order.
        Priority is Price (to create a min-heap).
        Tie-breaker is CreateTime.
        """
        return (order.Price, order.CreateTime, order)

    def can_match(self, buy_price: float) -> bool:
        """
        Checks if the best sell order (lowest price) is
        less than or equal to the incoming buy price.
        """
        best_sell = self.peek()
        return (best_sell is not None) and (best_sell.Price <= buy_price)