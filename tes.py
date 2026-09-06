import json
import unittest
from decimal import Decimal

from models import LoanAgreement, ColateralAssets, BorrowingStrategy


class MyTestCase(unittest.TestCase):

    def test_total_intrest_happy_senario(self):
        loan = LoanAgreement(
            loan_amount=Decimal("50000.00"),
            interest_rate=Decimal("0.055"),
            duration_days=30
        )

        total = Decimal("226.03")

        self.assertEqual(LoanAgreement.total_interest(loan), total)

    def test_total_repayment_happy_senario(self):
        loan = LoanAgreement(
            loan_amount=Decimal("50000.00"),
            interest_rate=Decimal("0.055"),
            duration_days=30
        )

        total = Decimal("50226.03")

        self.assertEqual(LoanAgreement.total_repayment(loan), total)

    def test_daily_cost_happy_senario(self):
        loan = LoanAgreement(
            loan_amount=Decimal("50000.00"),
            interest_rate=Decimal("0.055"),
            duration_days=30
        )

        total = Decimal("7.53")

        self.assertEqual(LoanAgreement.daily_cost(loan), total)


    def test_borrowable_amount(self):
        asset = ColateralAssets(
            asset_id = "abs",
            value = Decimal("100"),
            haircut = Decimal("0.10"),
            opportunity_cost = Decimal("2")
        )

        total = Decimal("90")

        self.assertEqual(asset.borrowable_amount, total)

    def test_should_borrow(self):
        loan = LoanAgreement(
            loan_amount=Decimal("50000.00"),
            interest_rate=Decimal("0.055"),
            duration_days=30
        )
        asset = ColateralAssets(
            asset_id="abs",
            value=Decimal("100"),
            haircut=Decimal("0.10"),
            opportunity_cost=Decimal("2")
        )

        borrow = BorrowingStrategy(
            loan, asset
        )

        self.assertFalse(BorrowingStrategy.should_borrow(borrow))


if __name__ == '__main__':
    unittest.main()
