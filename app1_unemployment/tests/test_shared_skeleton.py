"""Proof tests — App 1's Claim really runs on the shared skeleton engine.

These tests do not re-test unemployment rules (test_app1.py covers
those). They prove the refactor: a Claim's case is built from the
real skeleton Case / StepMachine / MoneyMove / Record, real money
moves through the engine's ledger exactly once per paid week, and
the DoublePayBlocked the app raises IS the skeleton's own class.
Stdlib unittest.
"""
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "skeleton"))

import skeleton
from skeleton import Case, MoneyMove, Record, StepMachine

from claim_flow import Claim, DoublePayBlocked


class TestClaimUsesRealEngine(unittest.TestCase):
    def test_case_is_built_on_skeleton_parts(self):
        claim = Claim(claimant="Test", wba=200)
        self.assertIsInstance(claim.case, Case)
        self.assertIsInstance(claim.case.machine, StepMachine)
        self.assertIsInstance(claim.case.ledger, MoneyMove)
        self.assertIsInstance(claim.case.record, Record)

    def test_case_record_and_rules_come_from_the_engine(self):
        claim = Claim(claimant="Test", wba=200)
        self.assertEqual(claim.case.record.get("claimant"), "Test")
        self.assertEqual(claim.case.record.get("wba"), 200)
        self.assertTrue(claim.case.rules.qualifies)
        self.assertEqual(claim.case.rules.amount_cents, 20000)

    def test_steps_move_on_the_engine_machine(self):
        claim = Claim(claimant="Test", wba=200)
        self.assertEqual(claim.state, "Filed")
        self.assertEqual(claim.case.current_step, "Filed")
        claim.certify_waiting_week()
        self.assertEqual(claim.state, "Certified")
        claim.certify_and_pay(week=1)
        self.assertEqual(claim.state, "Paid")
        self.assertEqual(
            claim.case.step_labels(),
            ["Filed", "WaitingWeek", "Certified", "Paid"],
        )


class TestMoneyMovesThroughEngine(unittest.TestCase):
    def test_engine_pay_called_once_per_paid_week_with_right_cents(self):
        calls = []
        original_pay = MoneyMove.pay

        def counting_pay(self, record_id, period, amount_cents):
            calls.append((period, amount_cents))
            return original_pay(self, record_id, period, amount_cents)

        MoneyMove.pay = counting_pay
        try:
            claim = Claim(claimant="Test", wba=200)
            claim.certify_waiting_week()  # unpaid — no engine pay
            claim.certify_and_pay(week=1)  # full week: $200.00
            claim.certify_and_pay(week=2, earnings=200.00)  # reduced: $50.00
        finally:
            MoneyMove.pay = original_pay

        self.assertEqual(calls, [("week-1", 20000), ("week-2", 5000)])
        # And the engine ledger itself holds exactly that money.
        self.assertEqual(claim.case.total_paid_cents(), 25000)
        self.assertTrue(claim.case.has_paid("week-1"))
        self.assertTrue(claim.case.has_paid("week-2"))
        self.assertFalse(claim.case.has_paid("week-0"))


class TestDoublePayBlockedIsSkeletonClass(unittest.TestCase):
    def test_identity(self):
        self.assertIs(DoublePayBlocked, skeleton.DoublePayBlocked)

    def test_second_pay_same_week_raises_and_moves_no_money(self):
        claim = Claim(claimant="Test", wba=200)
        claim.certify_waiting_week()
        claim.certify_and_pay(week=1)
        self.assertEqual(claim.total_paid, Decimal("200"))
        with self.assertRaises(skeleton.DoublePayBlocked):
            claim.certify_and_pay(week=1)
        self.assertEqual(claim.total_paid, Decimal("200"))
        self.assertEqual(claim.weeks_paid, 1)
        self.assertEqual(claim.case.total_paid_cents(), 20000)


if __name__ == "__main__":
    unittest.main()
