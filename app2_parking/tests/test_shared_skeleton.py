"""Proof tests: App 2 runs ON the shared skeleton engine, not a copy.

Run from the track folder:
    python3 -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "skeleton"))

from parking import PermitApplication, PermitOffice  # noqa: E402
from skeleton import Case, DoublePayBlocked, MoneyMove, StepMachine  # noqa: E402


def app(**overrides) -> PermitApplication:
    base = dict(driver="Ana Ruiz", plate="8XYZ123", address="12 Pine St",
                zone="North Lot", permit_type="resident")
    base.update(overrides)
    return PermitApplication(**base)


class TestRunsOnSharedEngine(unittest.TestCase):
    def test_stored_case_is_a_skeleton_case_on_the_shared_ledger(self):
        office = PermitOffice()
        result = office.submit(app())
        self.assertEqual(result.status, "Approved")

        case = office._cases[result.application_id]
        self.assertIsInstance(case, Case)
        self.assertIsInstance(case.machine, StepMachine)
        self.assertIsInstance(case.ledger, MoneyMove)
        # The case runs on the office's ONE shared ledger.
        self.assertIs(case.ledger, office._ledger)
        # The result's steps ARE the engine machine's step history.
        self.assertEqual(result.steps, case.step_labels())
        self.assertEqual(result.steps, ["Applied", "Checked", "Approved"])

    def test_all_cases_share_one_ledger(self):
        office = PermitOffice()
        first = office.submit(app())
        second = office.submit(app(plate="9ZZZ999", zone="Downtown"))
        self.assertIs(office._cases[first.application_id].ledger,
                      office._cases[second.application_id].ledger)


class TestEnginePayOnceGuard(unittest.TestCase):
    def test_engine_blocks_a_second_pay_for_the_same_period(self):
        office = PermitOffice()
        result = office.submit(app())
        self.assertEqual(result.fee, 30)

        case = office._cases[result.application_id]
        self.assertTrue(case.has_paid("permit-fee"))
        self.assertEqual(case.total_paid_cents(), 30 * 100)

        with self.assertRaises(DoublePayBlocked):
            case.pay(period="permit-fee", amount_cents=30 * 100)

        # The blocked second pay moved no money.
        self.assertEqual(case.total_paid_cents(), 30 * 100)
        self.assertEqual(
            office._ledger.total_paid_cents(case.record.id), 30 * 100)
        self.assertEqual(len(office.payments), 1)


class TestEnginePayCalledOnceAcrossDemoCases(unittest.TestCase):
    def test_spy_on_money_move_pay_counts_exactly_one_call(self):
        original_pay = MoneyMove.pay
        calls = {"count": 0}

        def counting_pay(self, record_id, period, amount_cents):
            calls["count"] += 1
            return original_pay(self, record_id, period, amount_cents)

        MoneyMove.pay = counting_pay
        try:
            office = PermitOffice()
            # The 3 demo-style cases: approved resident, denied zone,
            # exempt employee.
            approved = office.submit(app())
            denied = office.submit(app(
                driver="Ben Cole", plate="4ABC99", address="1 Far Away Rd",
                zone="Airport", permit_type="visitor"))
            exempt = office.submit(app(
                driver="Cy Park", plate="7EMP001", address="9 Oak Ave",
                zone="Downtown", permit_type="employee"))
        finally:
            MoneyMove.pay = original_pay

        self.assertEqual(approved.status, "Approved")
        self.assertEqual(denied.status, "Denied")
        self.assertEqual(exempt.status, "Approved")
        self.assertEqual(exempt.fee, 0)
        # Only the approved, fee-paying case ever reached the engine's pay.
        self.assertEqual(calls["count"], 1)
        self.assertEqual(len(office.payments), 1)


if __name__ == "__main__":
    unittest.main()
