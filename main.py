from ColateralOptimizer import ColateralOptimizer
from parser import DataParser

RAW_DATA = """[ {"asset_id": "UST_5Y",   "asset_class": "TREASURY", "currency": "USD", "value": "620000",   
"lot_size": "100000",   "opportunity_cost": "0.009"}, {"asset_id": "GILT_10Y", "asset_class": "GOVT_GBP", "currency": 
"GBP", "value": "450000",   "lot_size": "50000",    "opportunity_cost": "0.008"}, {"asset_id": "JGB_10Y",  
"asset_class": "GOVT_JPY", "currency": "JPY", "value": "70000000", "lot_size": "10000000", "opportunity_cost": 
"0.007"}, {"asset_id": "ODD_LOT",  "asset_class": "TREASURY", "currency": "USD", "value": "70000",    "lot_size": 
"100000",   "opportunity_cost": "0.006"} ] """


LENDER_RULES = """[
    {"lender_id": "ATLAS",    "rate": "0.041", "capacity": "700000", "day_count": 360,
     "haircuts": {"TREASURY": "0.02", "GOVT_GBP": "0.03"}, "fx_haircut_addon": "0.05"},
    {"lender_id": "MERIDIAN", "rate": "0.046", "capacity": "900000", "day_count": 360,
     "haircuts": {"TREASURY": "0.02", "GOVT_GBP": "0.04", "GOVT_JPY": "0.04"}, "fx_haircut_addon": "0.06"}
]"""

class main():
    parser = DataParser(file = RAW_DATA, rules = LENDER_RULES)
    rules = parser.parse_lender_rules()
    data  = parser.get_valid_assets()
    #print(rules,data)

    algorithm = ColateralOptimizer(data = data , loan = rules, required_cash = 1200000, days = 21)

    print(algorithm.greedy_algorith())



if __name__ == "__main__":
    main()


