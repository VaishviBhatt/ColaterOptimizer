# Collateral Optimizer

A high-performance Python backend service designed to optimize multi-lender collateral allocation, handle complex foreign exchange (FX) conversions, apply asset haircuts, and solve target-matching financial constraints.

## Key Features
* **Dual Optimization Strategies:** Implements both a **Greedy Algorithm** (for multi-lender capacity matching, efficient asset drawdown using `deque`, and interest calculations) and a **Dynamic Programming (Knapsack)** approach to solve exact target-matching under concentration limits.
* **Financial Precision:** Utilizes Python's `decimal.Decimal` and strict rounding rules (`ROUND_DOWN`) to eliminate floating-point inaccuracies in financial calculations.
* **Performance & State Management:** Tracks local asset balances and multi-lender capacities efficiently with $O(1)$ queue operations and fast dictionary lookups.
