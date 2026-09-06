from dataclasses import dataclass, field
from decimal import Decimal

from typing import Any, Dict

@dataclass
class ColateralAssets:
    asset_id : str
    value : Decimal
    asset_class : str
    currency : str
    lot_size : Decimal
    opportunity_cost : Decimal





@dataclass
class LenderRules:
    lender_id : str
    rate : Decimal
    capacity : Decimal
    day_count : int
    haircuts : Dict[str , Decimal]
    fx_haircut_addon : Decimal

    def total_haircut(self, asset: ColateralAssets) -> Decimal | None:
        if asset.asset_class not in self.haircuts:
            return None

        base_haircut = self.haircuts[asset.asset_class]

        # Validate base haircut range
        if not (Decimal("0.00") <= base_haircut < Decimal("1.00")):
            raise ValueError("Base haircut out of valid range [0, 1)")

        # Add FX haircut addon only for non-USD currencies
        addon = self.fx_haircut_addon if asset.currency != "USD" else Decimal("0.00")

        total = base_haircut + addon
        if total >= Decimal("1.00"):
            return None

        return total


    def effective_value(self, asset : ColateralAssets) -> Decimal:

        if asset.value < Decimal("0.00"):
            return Decimal("0.00")

        haircut = self.total_haircut(asset)
        if haircut is None:
            return Decimal("0.00")

        return asset.value * (Decimal("1.00") - haircut)

    def total_borrowed(self, money_borrowed : Decimal, days : int) -> Decimal:
        if money_borrowed < Decimal("0.00"):
            raise ValueError ("money borrowed less than 0")

        repo_rate = self.rate * (Decimal(days)/Decimal(self.day_count))

        return money_borrowed * repo_rate


    def lot_calculation(self, fx_rate: Decimal, amount: Decimal, asset: ColateralAssets) -> Decimal:

        haircut = self.total_haircut(asset)

        if haircut is None:
            return Decimal("0.00")

        # 1. Multiplier = FX * (1 - Total Haircut)
        multiplier = fx_rate * (Decimal("1.00") - haircut)

        # Avoid division by zero
        if multiplier <= Decimal("0.00"):
            return Decimal("0.00")

        # 2. Convert USD bottleneck cash to raw native units needed
        native_units_needed = amount / multiplier

        # 3. Floor raw native units by lot size to get full blocks
        full_blocks = native_units_needed // asset.lot_size

        # 4. Multiply blocks back by lot size to get valid native units
        valid_native_units = full_blocks * asset.lot_size

        # 5. Multiply valid native units by multiplier to get final USD cash
        usd_cash_pledged = valid_native_units * multiplier

        return usd_cash_pledged


def convert_fx(from_ccy: str, to_ccy: str) -> Decimal:
    quotes = [
    {"from": "GBP", "to": "USD", "rate": "1.27"},
    {"from": "EUR", "to": "USD", "rate": "1.08"},
    {"from": "USD", "to": "JPY", "rate": "148.5"}
]
    """Returns the FX rate to convert 1 unit of from_ccy into to_ccy as a Decimal."""
    if from_ccy == to_ccy:
        return Decimal("1")

    for q in quotes:
        rate = Decimal(str(q["rate"]))
        q_from, q_to = q["from"], q["to"]

        # Exact match
        if q_from == from_ccy and q_to == to_ccy:
            return rate
        # Inverted match
        if q_from == to_ccy and q_to == from_ccy:
            return Decimal("1") / rate

    raise ValueError(f"No valid FX quote route found from {from_ccy} to {to_ccy}")