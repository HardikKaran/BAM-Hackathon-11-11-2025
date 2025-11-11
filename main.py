"""
Main entry point for running a step-by-step demonstration
of the OrderMatchingEngine, based on the problem specification.

To run the automated tests, use `pytest`.
This file is for demonstration purposes only.
"""

from datetime import datetime, timedelta

# Note the updated import paths
from matching_engine.models import Order, Side
from matching_engine.engine import OrderMatchingEngine
from matching_engine.order_book import OrderBook

def print_books(engine: OrderMatchingEngine):
    """Helper function to print the current state of the order books."""
    
    # A safe way to print the contents of a heap-based book is
    # to pop all items, store them, print, and add them back.
    # For simplicity here, we'll just peek at the best.
    
    buy_best = engine.buy_book.peek()
    sell_best = engine.sell_book.peek()
    
    buy_str = f"{buy_best.OrderID} ({buy_best.Quantity}) @ {buy_best.Price}" if buy_best else "[]"
    sell_str = f"{sell_best.OrderID} ({sell_best.Quantity}) @ {sell_best.Price}" if sell_best else "[]"

    print(f"  Best Buy:  {buy_str}")
    print(f"  Best Sell: {sell_str}\n")


def run_example():
    """Runs the full example from the task markdown file."""
    
    engine = OrderMatchingEngine()
    
    # We use a base time and increment it for each order to simulate time priority
    base_time = datetime(2025, 1, 1, 12, 0, 0)
    
    test_orders = [
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
    
    print("--- Starting Matching Engine Demonstration ---")
    
    for order in test_orders:
        print(f"--- Processing {order.Side.value} {order.OrderID} (Price: {order.Price}, Qty: {order.Quantity}) ---")
        
        executions = engine.process_order(order)
        
        if not executions:
            print("  No Executions")
        else:
            print("  Executions:")
            for exec in executions:
                print(f"  - ExecID: {exec.ExecutionID}, Price: {exec.Price}, Qty: {exec.Quantity}")
                print(f"    (Buy: {exec.Buy_OrderID}, Sell: {exec.Sell_OrderID})")
                
        print_books(engine)

if __name__ == "__main__":
    run_example()