"""
The core OrderMatchingEngine.

This class orchestrates the matching process by coordinating
between a BuyBook and a SellBook.
"""

from typing import List

from .models import Order, Execution, Side
from .order_book import BuyBook, SellBook

class OrderMatchingEngine:
    """
    Manages the order books and processes new incoming orders.
    
    This class is responsible for:
    1. Holding the BuyBook and SellBook.
    2. Generating unique Execution IDs.
    3. Receiving a new order and matching it against the opposite book.
    4. Placing any unfilled quantity of the new order into the correct book.
    5. Returning all executions that were generated.
    """
    
    def __init__(self):
        self.buy_book = BuyBook()
        self.sell_book = SellBook()
        self._next_execution_id = 1

    def _generate_execution_id(self) -> int:
        """Atomically generates the next sequential execution ID."""
        exec_id = self._next_execution_id
        self._next_execution_id += 1
        return exec_id

    def process_order(self, order: Order) -> List[Execution]:
        """
        Processes a new order, matching it against the
        opposite book and returning any executions.

        Args:
            order: The new Order object to be processed.

        Returns:
            A list of Execution objects, which is empty
            if no matches occurred.
        """
        created_executions: List[Execution] = []
        
        if order.Side == Side.BUY:
            self._match(order, self.sell_book, self.buy_book, created_executions)
        else: # order.Side == Side.SELL
            self._match(order, self.buy_book, self.sell_book, created_executions)
        
        # If the incoming order is not fully filled, add it to its book
        if order.Quantity > 0:
            if order.Side == Side.BUY:
                self.buy_book.add(order)
            else:
                self.sell_book.add(order)
                
        return created_executions

    def _match(self, 
               incoming_order: Order, 
               opposite_book: BuyBook | SellBook,
               own_book: BuyBook | SellBook, 
               created_executions: List[Execution]):
        """
        The generic matching loop.
        
        This loop runs as long as the incoming order has quantity
        and can be matched with the best-priority order in the
        opposite book.

        Args:
            incoming_order: The new order being processed.
            opposite_book: The book to match against (e.g., SellBook for a Buy).
            own_book: The book to place the remainder in (e.g., BuyBook for a Buy).
            created_executions: The list to append new Executions to.
        """
        
        while incoming_order.Quantity > 0 and opposite_book.can_match(incoming_order.Price):
            
            # Get the best-priority resting order
            resting_order = opposite_book.pop()
            if not resting_order:
                break # Should be impossible due to can_match(), but safe
            
            # Determine execution quantity and price
            execution_quantity = min(incoming_order.Quantity, resting_order.Quantity)
            
            # Price is *always* that of the resting order
            execution_price = resting_order.Price 
            
            # Create execution
            exec_id = self._generate_execution_id()
            if incoming_order.Side == Side.BUY:
                execution = Execution(
                    ExecutionID=exec_id,
                    Price=execution_price,
                    Quantity=execution_quantity,
                    Sell_OrderID=resting_order.OrderID,
                    Buy_OrderID=incoming_order.OrderID
                )
            else: # incoming_order.Side == Side.SELL
                execution = Execution(
                    ExecutionID=exec_id,
                    Price=execution_price,
                    Quantity=execution_quantity,
                    Sell_OrderID=incoming_order.OrderID,
                    Buy_OrderID=resting_order.OrderID
                )
            created_executions.append(execution)
            
            # Update quantities
            incoming_order.Quantity -= execution_quantity
            resting_order.Quantity -= execution_quantity
            
            # If the resting order is not fully filled, put it back
            if resting_order.Quantity > 0:
                opposite_book.add(resting_order)