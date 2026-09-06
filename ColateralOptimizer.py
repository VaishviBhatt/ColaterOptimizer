import heapq
from collections import deque
from decimal import Decimal, ROUND_DOWN
from typing import Any

from models import LenderRules, ColateralAssets, convert_fx


class ColateralOptimizer:
    def __init__(self, data: list[ColateralAssets], loan: list[LenderRules], required_cash: int, days: int):
        self.data = data
        self.loan = loan
        self.required_cash = required_cash
        self.days = days

    def greedy_algorith(self) -> list[dict[str: str | Any]]:

        current_amount = Decimal(self.required_cash)

        allocated = []

        # Local state dictionary tracking remaining value per asset ID
        asset_balances = {
            a.asset_id: Decimal(str(a.value))
            for a in self.data
            if Decimal(str(a.value)) > Decimal("0.00")
        }

        # Fast lookup mapping for asset objects
        asset_map = {a.asset_id: a for a in self.data if a.asset_id in asset_balances}

        # Use deque for O(1) popleft operations
        lenders = deque(sorted(self.loan, key=lambda x: x.capacity))


        while lenders  and current_amount > Decimal("0.00"):

            lender = lenders.popleft()

            capacity = lender.capacity

            # Filter and sort using local balance map instead of mutating dataclasses
            valid_asset_ids = [
                aid for aid, remaining_val in asset_balances.items()
                if remaining_val > Decimal("0.00") and lender.total_haircut(asset_map[aid]) is not None
            ]

            local_assets = deque(
                sorted(
                    [asset_map[aid] for aid in valid_asset_ids],
                    key=lambda x: lender.effective_value(x) * convert_fx(x.currency, "USD"),
                    reverse=True
                )
            )
            while capacity > Decimal("0.00") and local_assets and current_amount > Decimal("0.00"):

                asset = local_assets.popleft()

                fx_rate = convert_fx(asset.currency, "USD")

                effective_value = lender.effective_value(asset) * fx_rate

                cash_borrowed = min(effective_value, capacity, current_amount)

                cash_borrowed_lot = lender.lot_calculation(fx_rate, cash_borrowed, asset)

                if cash_borrowed_lot <= Decimal("0.00"):
                    continue

                total_after_intrest = lender.total_borrowed(cash_borrowed_lot, self.days)

                #update state

                capacity -= cash_borrowed_lot
                current_amount -= cash_borrowed_lot

                asset_balances[asset.asset_id] -= cash_borrowed_lot

                allocated.append(
                    {
                        "asset_id" : asset.asset_id,
                        "lender_id" : lender.lender_id,
                        "amount_borrowed_USD" : cash_borrowed_lot.quantize(Decimal("1"), rounding= ROUND_DOWN),
                        "total_after_intrest" : total_after_intrest.quantize(Decimal("1"), rounding= ROUND_DOWN)
                    }
                )

        if current_amount == Decimal("0.00"):
            raise ValueError ( "No collateral raised")

        return allocated





    def knapsack(self) -> list[dict[str: str | Decimal]]:

        target = int(self.required_cash)
        max_concentration = self.required_cash * self.loan.max_concentration

        assets = [
            (asset, min(int(asset.borrowable_amount), max_concentration))
            for _cost, _id, asset in self.data
        ]

        dp = [False] * (target + 1)
        dp[0] = True
        chosen: list[list] = [[] for _ in range(target + 1)]

        for asset, w in assets:
            if w <= 0:
                continue

            # Traverse backwards to prevent re-using the same asset multiple times
            for j in range(target - w, -1, -1):
                if dp[j]:
                    new_j = j + w
                    if not dp[new_j]:
                        dp[new_j] = True
                        chosen[new_j] = chosen[j] + [
                            {"asset": asset, "allocated_weight": Decimal(w)}
                        ]

        if not dp[target]:
            raise ValueError(
                "Insufficient funds or cannot match exact target with given constraints."
            )

        return [
            {
                "asset_id": item["asset"].asset_id,
                "borrowable_amount": item["allocated_weight"],
            }
            for item in chosen[target]
        ]
