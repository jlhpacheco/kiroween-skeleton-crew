"""Tests for App 1 — WBA table, base period, claim flow. Stdlib unittest."""
import datetime
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from base_period import alternate_base_period, standard_base_period
from claim_flow import Claim, ClaimError, DoublePayBlocked, weekly_payment
from wba import max_benefit_amount, monetarily_qualifies, weekly_benefit_amount


class TestWBA(unittest.TestCase):
    def test_table_low_edge(self):
        self.assertEqual(weekly_benefit_amount(900.00), 40)

    def test_table_first_bracket_top(self):
        self.assertEqual(weekly_benefit_amount(948.99), 40)
        self.assertEqual(weekly_benefit_amount(949.00), 41)

    def test_table_top_edge(self):
        self.assertEqual(weekly_benefit_amount(1832.99), 70)

    def test_above_table_formula_rounds_up(self):
        # 1833.00 / 26 = 70.5 -> ceil = 71
        self.assertEqual(weekly_benefit_amount(1833.00), 71)

    def test_mid_wages_formula(self):
        # 5200 / 26 = 200 exactly
        self.assertEqual(weekly_benefit_amount(5200.00), 200)

    def test_cap_450(self):
        self.assertEqual(weekly_benefit_amount(20000.00), 450)
        self.assertEqual(weekly_benefit_amount(11700.00), 450)

    def test_below_table_returns_zero(self):
        self.assertEqual(weekly_benefit_amount(899.99), 0)

    def test_max_benefit_at_cap(self):
        self.assertEqual(max_benefit_amount(450), 11700)


class TestQualify(unittest.TestCase):
    def test_899_fails_first_branch_and_second(self):
        # $899 high quarter: below $1,300 (branch A) and below $900 (branch B)
        self.assertFalse(monetarily_qualifies(899.00, 899.00 * 4))

    def test_branch_a_high_quarter_1300(self):
        self.assertTrue(monetarily_qualifies(1300.00, 1300.00))

    def test_branch_b_900_plus_125_percent(self):
        self.assertTrue(monetarily_qualifies(900.00, 1125.00))

    def test_branch_b_fails_without_total(self):
        self.assertFalse(monetarily_qualifies(900.00, 1000.00))


class TestBasePeriod(unittest.TestCase):
    def test_jan_mar_ends_sep_30_prior(self):
        p = standard_base_period(datetime.date(2026, 2, 1))
        self.assertEqual(p["end"], datetime.date(2025, 9, 30))
        self.assertEqual(len(p["quarters"]), 4)

    def test_apr_jun_ends_dec_31_prior(self):
        p = standard_base_period(datetime.date(2026, 5, 1))
        self.assertEqual(p["end"], datetime.date(2025, 12, 31))

    def test_jul_sep_ends_mar_31(self):
        p = standard_base_period(datetime.date(2026, 8, 1))
        self.assertEqual(p["end"], datetime.date(2026, 3, 31))

    def test_oct_dec_ends_jun_30(self):
        p = standard_base_period(datetime.date(2026, 11, 2))
        self.assertEqual(p["end"], datetime.date(2026, 6, 30))
        self.assertEqual(p["start"], datetime.date(2025, 7, 1))

    def test_alternate_is_most_recent_four(self):
        p = alternate_base_period(datetime.date(2026, 11, 2))
        self.assertEqual(p["end"], datetime.date(2026, 9, 30))


class TestClaimFlow(unittest.TestCase):
    def _claim(self):
        c = Claim(claimant="Test", wba=200)
        c.certify_waiting_week()
        return c

    def test_waiting_week_unpaid(self):
        c = Claim(claimant="Test", wba=200)
        paid = c.certify_waiting_week()
        self.assertEqual(paid, Decimal("0"))
        self.assertEqual(c.total_paid, Decimal("0"))
        self.assertEqual(c.payments[0].amount, Decimal("0"))

    def test_paid_week_requires_waiting_week(self):
        c = Claim(claimant="Test", wba=200)
        with self.assertRaises(ClaimError):
            c.certify_and_pay(week=1)

    def test_full_week_pays_wba(self):
        c = self._claim()
        p = c.certify_and_pay(week=1)
        self.assertEqual(p.amount, Decimal("200"))

    def test_partial_earnings_quarter_disregard(self):
        # Earnings $200: disregard = max($25, 25% of $200 = $50) = $50;
        # deduction $150; WBA $200 -> pays $50.
        self.assertEqual(weekly_payment(200, 200.00), Decimal("50"))

    def test_partial_earnings_25_dollar_disregard(self):
        # Earnings $80: 25% = $20, so $25 disregard wins; deduction $55;
        # WBA $200 -> pays $145.
        self.assertEqual(weekly_payment(200, 80.00), Decimal("145"))

    def test_small_earnings_fully_disregarded(self):
        # Earnings $20 < $25 disregard -> no deduction.
        self.assertEqual(weekly_payment(200, 20.00), Decimal("200"))

    def test_double_pay_blocked(self):
        c = self._claim()
        c.certify_and_pay(week=1)
        with self.assertRaises(DoublePayBlocked):
            c.certify_and_pay(week=1)
        self.assertEqual(c.total_paid, Decimal("200"))  # no money moved twice
        self.assertEqual(c.weeks_paid, 1)

    def test_26_week_cap(self):
        c = self._claim()
        for w in range(1, 27):
            c.certify_and_pay(week=w)
        self.assertEqual(c.weeks_paid, 26)
        self.assertEqual(c.total_paid, Decimal(26 * 200))
        with self.assertRaises((ClaimError, DoublePayBlocked)):
            c.certify_and_pay(week=26)


if __name__ == "__main__":
    unittest.main()
