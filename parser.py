
import json
from decimal import Decimal, InvalidOperation
from typing import Dict
from typing import List

from models import LenderRules, ColateralAssets


class DataParser:
    def __init__(self, file: str, rules: str):
        self.file = file
        self.rules = rules

    def parse_lender_rules(self) -> List[LenderRules]:
        data = json.loads(self.rules)
        rules: List[LenderRules] = []

        for rule in data:
            try:
                raw_haircuts = rule.get("haircuts", {})
                haircuts: Dict[str, Decimal] = {
                    str(asset_class): Decimal(str(rate))
                    for asset_class, rate in raw_haircuts.items()
                }

                raw_rules = rule.get("rules", {})
                parsed_rules = {
                    "min_borrowable_per_asset": Decimal(str(raw_rules.get("min_borrowable_per_asset", "0"))),
                    "max_single_asset_pct_of_loan": Decimal(str(raw_rules.get("max_single_asset_pct_of_loan", "1.00"))),
                }

                lender = LenderRules(
                    lender_id=str(rule["lender_id"]),
                    rate=Decimal(str(rule["rate"])),
                    capacity=Decimal(str(rule["capacity"])),
                    day_count=int(rule["day_count"]),
                    haircuts=haircuts,
                    fx_haircut_addon = Decimal(str(rule["fx_haircut_addon"])),
                )
                rules.append(lender)
            except (ValueError, InvalidOperation, KeyError, TypeError):
                continue

        return rules

    def get_valid_assets(self) -> list[ColateralAssets]:
        data = json.loads(self.file)
        valid_assets = []

        for item in data:
            try:
                asset = ColateralAssets(
                    asset_id=str(item["asset_id"]),
                    value=Decimal(str(item["value"])),
                    asset_class = str(item["asset_class"]),
                    currency=str(item["currency"]),
                    lot_size = Decimal(str(item["lot_size"])),
                    opportunity_cost = Decimal(str(item["opportunity_cost"]))
                )
                valid_assets.append(asset)
            except(KeyError, ValueError, InvalidOperation, TypeError):
                continue

        return valid_assets
