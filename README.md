# BAM-Hackathon-11-11-2025
Balyasny Asset Management Hackathon in Imperial College London 11/11/2025

REQUIREMENTS: 
-pytest

Price-Time Priority Matching Engine

Author: [Your Name Here]
Event: BAM Hackathon (November 2025)

1. Project Overview

This project is a Python-based implementation of a high-speed, in-memory matching engine for financial orders. It adheres to the price-time priority matching algorithm, which is the foundational mechanism for most modern stock exchanges.

The engine is built to satisfy the requirements of the hackathon task:

Accepts new Order objects.

Matches incoming orders against a-book of resting orders.

Prioritizes matches based on the best price (highest for buys, lowest for sells) and then by the earliest CreateTime.

Generates a list of Execution objects for every match that occurs.

Maintains the state of two separate order books (Buy and Sell).

2. Core Logic & Architecture

The solution is built using an encapsulated, object-oriented design to ensure maintainability, testability, and clarity.

Data Structure: The core of each order book (BuyBook and SellBook) is a priority queue (min-heap), provided by Python's built-in heapq module. This is the ideal data structure as it provides O(log n) for insertions and O(1) for peeking at the best-priority order.

Buy Book (Max-Heap): To achieve max-priority (highest price first), we store the (-price, create_time, order) tuple, effectively inverting the min-heap's behavior.

Sell Book (Min-Heap): To achieve min-priority (lowest price first), we store the (price, create_time, order) tuple.

Architecture: The project is divided into three logical components:

models.py: Contains the simple data classes (Order, Execution, Side) that act as data transfer objects.

order_book.py: Encapsulates all the heap logic into BuyBook and SellBook classes. This abstraction hides the implementation details from the engine.

engine.py: The OrderMatchingEngine class, which acts as a coordinator. It receives new orders and delegates the matching and storage logic to the OrderBook instances.

3. Project Structure

BAM-HACKATHON-11-11-2025/
│
├── matching_engine/          # Main Python package for the engine
│   ├── __init__.py
│   ├── models.py           # Defines Order, Execution, and Side objects
│   ├── order_book.py       # Defines the BuyBook and SellBook classes
│   └── engine.py           # Defines the main OrderMatchingEngine class
│
├── tests/
│   ├── __init__.py
│   └── test_engine.py      # Pytest unit tests for all logic
│
├── main.py                 # A demonstration script to run the example
├── requirements.txt        # Project dependencies
└── README.md               # This file


4. Installation

Clone the repository:

git clone [your-repo-url]
cd BAM-HACKATHON-11-11-2025


(Optional but recommended) Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:
The only external dependency is pytest for testing.

pip install -r requirements.txt


5. How to Run

There are two ways to run the code: the step-by-step demo or the automated test suite.

A. Run the Demonstration

This script runs the exact 10-order example from the hackathon's task.md file and prints the status of the order books and any executions at each step.

From the project root directory, run:

python main.py


You will see output that mirrors the example table, starting with:

--- Starting Matching Engine Demonstration ---
--- Processing Buy Buy-1 (Price: 9.99, Qty: 300) ---
  No Executions
  Best Buy:  Buy-1 (300) @ 9.99
  Best Sell: []
...


B. Run the Automated Tests (Recommended)

This is the best way to verify correctness. The test suite includes 8 tests that cover simple placements, full fills, partial fills, price priority, time priority, and the entire 10-order example.

From the project root directory, run:

pytest


If all tests pass, you will see a green output:

========= 8 passed in 0.01s =========
