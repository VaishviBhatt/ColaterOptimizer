import unittest
from decimal import Decimal
from parser import DataParser
from models import ColateralAssets


class MyTestCase(unittest.TestCase):
    def test_parser_return_correct_data_andignores_unwanted(self):
        RAW_DATA = """[
            {"asset_id": "GOVT_UK_GILT_10Y",  "value": "600000.00", "haircut": "0.03", "opportunity_cost": "0.012"},
            {"asset_id": "GOVT_US_TIPS",      "value": "400000.00", "haircut": "0.04", "opportunity_cost": "0.018"},
            {"asset_id": "BROKEN_BOND",       "value": "str", "haircut": "1.00", "opportunity_cost": "0.015"}
            ]"""

        RULES = """{
                      "accepted_prefixes": [
                        "GOVT",
                        "CORP_BOND_IG"
                      ],
                      "min_borrowable": "50000.00",
                      "max_concentration": "0.60",
                      "intrest_rate": "0.055",
                      "duration_days": 30,
                      "max_ltv": "0.80"
                    }"""

        expected = [
            ColateralAssets(
                asset_id= "GOVT_UK_GILT_10Y",
                value= Decimal("600000.00"),
                haircut= Decimal("0.03"),
                opportunity_cost= Decimal("0.012")),
            ColateralAssets(
                asset_id= "GOVT_US_TIPS",
                value= Decimal("400000.00"),
                haircut= Decimal("0.04"),
                opportunity_cost= Decimal("0.018"))]

        parser = DataParser(file=RAW_DATA, rules=RULES)

        rules = parser.parse_lender_rules()
        actual = parser.get_valid_assets(rules)

        self.assertListEqual(actual,expected)


if __name__ == '__main__':
    unittest.main()
