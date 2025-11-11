"""
Unit test suite for the OrderMatchingEngine.

This suite validates all core functionality, including:
- Price-Time priority
- Simple and partial fills
- Multi-fill orders
- Correct order book state
- The full example from the specification
"""

import pytest
from datetime import datetime, timedelta

# Update imports to reflect the new 'src' structure
from matching_engine.models import Order, Side
from matching_engine.engine import OrderMatchingEngine

@pytest.fixture
def engine() -> OrderMatchingEngine:
    """Pytest fixture to provide a clean engine for each test."""
    return OrderMatchingEngine()

@pytest.fixture
def base_time() -> datetime:
    """Pytest fixture to provide a consistent starting time."""
    return datetime(2025, 1, 1, 12, 0, 0)


def test_simple_order_placement(engine, base_time):
    """Test that an order with no match is placed in the correct book."""
    buy_order = Order("B1", base_time, Side.BUY, 99.0, 100)
    executions = engine.process_order(buy_order)
    
    assert not executions
    assert not engine.sell_book.is_empty()
    assert engine.buy_book.peek().OrderID == "B1"

def test_simple_match_full(engine, base_time):
    """Test a simple, complete match between two orders."""
    buy_order = Order("B1", base_time, Side.BUY, 100.0, 100)
    sell_order = Order("S1", base_time + timedelta(seconds=1), Side.SELL, 100.0, 100)
    
    engine.process_order(buy_order)
    executions = engine.process_order(sell_order)
    
    assert len(executions) == 1
    assert executions[0].Price == 100.0
    assert executions[0].Quantity == 100
    assert executions[0].Buy_OrderID == "B1"
    assert executions[0].Sell_OrderID == "S1"
    
    assert engine.buy_book.is_empty()
    assert engine.sell_book.is_empty()

def test_partial_match_incoming(engine, base_time):
    """Test a match that partially fills the resting order."""
    engine.process_order(Order("B1", base_time, Side.BUY, 100.0, 200))
    
    sell_order = Order("S1", base_time + timedelta(seconds=1), Side.SELL, 100.0, 50)
    executions = engine.process_order(sell_order)

    assert len(executions) == 1
    assert executions[0].Quantity == 50
    assert engine.buy_book.peek().Quantity == 150 # 200 - 50
    assert engine.sell_book.is_empty()

def test_partial_match_resting(engine, base_time):
    """Test a match that partially fills the incoming order."""
    engine.process_order(Order("B1", base_time, Side.BUY, 100.0, 100))
    
    sell_order = Order("S1", base_time + timedelta(seconds=1), Side.SELL, 100.0, 150)
    executions = engine.process_order(sell_order)

    assert len(executions) == 1
    assert executions[0].Quantity == 100
    assert engine.buy_book.is_empty()
    assert engine.sell_book.peek().OrderID == "S1"
    assert engine.sell_book.peek().Quantity == 50 # 150 - 100

def test_price_priority_buy_side(engine, base_time):
    """Test that an incoming sell hits the highest-priced buy first."""
    engine.process_order(Order("B1-low", base_time, Side.BUY, 99.0, 100))
    engine.process_order(Order("B2-high", base_time + timedelta(seconds=1), Side.BUY, 100.0, 100))
    
    sell_order = Order("S1", base_time + timedelta(seconds=2), Side.SELL, 100.0, 100)
    executions = engine.process_order(sell_order)

    assert len(executions) == 1
    assert executions[0].Buy_OrderID == "B2-high" # Matched with higher price
    assert engine.buy_book.peek().OrderID == "B1-low" # Lower price order remains
    
def test_time_priority(engine, base_time):
    """Test that orders at the same price are matched by time (FIFO)."""
    engine.process_order(Order("B1-first", base_time, Side.BUY, 100.0, 50))
    engine.process_order(Order("B2-second", base_time + timedelta(seconds=1), Side.BUY, 100.0, 50))
    
    sell_order = Order("S1", base_time + timedelta(seconds=2), Side.SELL, 100.0, 75)
    executions = engine.process_order(sell_order)

    assert len(executions) == 2
    # First execution is with the first order
    assert executions[0].Buy_OrderID == "B1-first"
    assert executions[0].Quantity == 50
    
    # Second execution is with the second order
    assert executions[1].Buy_OrderID == "B2-second"
    assert executions[1].Quantity == 25
    
    # B2-second remains in the book with 25 quantity
    assert engine.buy_book.peek().OrderID == "B2-second"
    assert engine.buy_book.peek().Quantity == 25

def test_no_match_price(engine, base_time):
    """Test that orders do not match if prices are incompatible."""
    engine.process_order(Order("B1", base_time, Side.BUY, 99.0, 100))
    sell_order = Order("S1", base_time + timedelta(seconds=1), Side.SELL, 100.0, 100)
    executions = engine.process_order(sell_order)
    
    assert not executions
    assert engine.buy_book.peek().OrderID == "B1"
    assert engine.sell_book.peek().OrderID == "S1"

def test_full_example_from_markdown(engine, base_time):
    """Runs the complete scenario from the problem description and asserts the final state."""
    
    orders = [
        Order(OrderID="Buy-1",  Side=Side.BUY,  Price=9.99,  Quantity=300, CreateTime=base_time + timedelta(seconds=1)),
        Order(OrderID="Buy-2",  Side=Side.BUY,  Price=10.00, Quantity=200, CreateTime=base_time + timedelta(seconds=2)),
        Order(OrderID="Sell-1", Side=Side.SELL, Price=10.01, Quantity=300, CreateTime=base_time + timedelta(seconds=3)),
        Order(OrderID="Sell-2", Side=Side.SELL, Price=10.00, Quantity=100, CreateTime=base_time + timedelta(seconds=4)),
        Order(OrderID="Sell-3", Side=Side.SELL, Price=9.99,  Quantity=200, CreateTime=base_time + timedelta(seconds=5)),
        Order(OrderID="Sell-4", Side=Side.SELL, Price=10.00, Quantity=200, CreateTime=base_time + timedelta(seconds=6)),
        Order(OrderID="Buy-3",  Side=Side.BUY,  Price=10.00, Quantity=300, CreateTime=base_time + timedelta(seconds=7)),
        Order(OrderID="Sell-5", Side=Side.SELL, Price=10.01, Quantity=500, CreateTime=base_time + timedelta(seconds=8)),
        Order(OrderID="Buy-4",  Side=Side.BUY,  Price=10.01, Quantity=200, CreateTime=base_time + timedelta(seconds=9)),
        Order(OrderID="Buy-5",  Side=Side.BUY,  Price=10.01, Quantity=300, CreateTime=base_time + timedelta(seconds=10)),
    ]
    
    total_executions = 0
    for order in orders:
        executions = engine.process_order(order)
        total_executions += len(executions)

    # Final assertions based on the example table
    assert total_executions == 7
    
    # Final Buy Book State: Buy-3 (100) @ 10.00, Buy-1 (200) @ 9.99
    buy_orders = [engine.buy_book.pop() for _ in range(2)]
    buy_orders_map = {o.OrderID: o for o in buy_orders}
    
    assert buy_orders_map["Buy-3"].Quantity == 100
    assert buy_orders_map["Buy-3"].Price == 10.00
    assert buy_orders_map["Buy-1"].Quantity == 200
    assert buy_orders_map["Buy-1"].Price == 9.99
    assert engine.buy_book.is_empty()

    # Final Sell Book State: Sell-5 (300) @ 10.01
    assert engine.sell_book.peek().OrderID == "Sell-5"
    assert engine.sell_book.peek().Quantity == 300
    engine.sell_book.pop()
    assert engine.sell_book.is_empty()