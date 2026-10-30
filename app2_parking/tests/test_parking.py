"""Tests for App 2 — Parking Permits. Stdlib unittest only.

Run from the track folder:
    python3 -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parking import RULES, PermitApplication, PermitOffice  # noqa: E402


def app(**overrides) -> PermitApplication:
    base = dict(driver="Ana Ruiz", plate="8XYZ123", address="12 Pine St",
                zone="North Lot", permit_type="resident")
    base.update(overrides)
    return PermitApplication(**base)


class TestApprovedAndPaid(unittest.TestCase):
    def test_resident_approved_fee_30_paid_once(self):
        office = PermitOffice()
        result = office.submit(app())
        self.assertEqual(result.status, "Approved")
        self.assertEqual(result.fee, 30)
        self.assertEqual(result.steps, ["Applied", "Checked", "Approved"])
        self.assertIsNotNone(result.payment)
        self.assertEqual(result.payment.amount, 30)
        self.assertEqual(len(office.payments), 1)

    def test_visitor_fee_10(self):
        office = PermitOffice()
        result = office.submit(app(permit_type="visitor"))
        self.assertEqual(result.status, "Approved")
        self.assertEqual(result.fee, 10)
        self.assertEqual(result.payment.amount, 10)

    def test_payment_is_idempotent(self):
        office = PermitOffice()
        result = office.submit(app())
        first = result.payment
        again = office.pay(result.application_id)
        self.assertIs(again, first)
        self.assertEqual(len(office.payments), 1)
        self.assertEqual(office.payments[result.application_id].amount, 30)


class TestDenied(unittest.TestCase):
    def test_denied_zone_not_allowed_no_money(self):
        office = PermitOffice()
        result = office.submit(app(zone="Airport"))
        self.assertEqual(result.status, "Denied")
        self.assertEqual(result.steps, ["Applied", "Checked", "Denied"])
        self.assertTrue(any("not in an allowed zone" in r for r in result.reasons))
        self.assertIsNone(result.payment)
        self.assertEqual(len(office.payments), 0)

    def test_denied_plate_too_short(self):
        office = PermitOffice()
        result = office.submit(app(plate="AB1"))
        self.assertEqual(result.status, "Denied")
        self.assertTrue(any("4-10 characters" in r for r in result.reasons))

    def test_denied_plate_bad_characters(self):
        office = PermitOffice()
        result = office.submit(app(plate="AB!123"))
        self.assertEqual(result.status, "Denied")
        self.assertTrue(any("letters and numbers only" in r for r in result.reasons))

    def test_denied_unknown_permit_type(self):
        office = PermitOffice()
        result = office.submit(app(permit_type="vip"))
        self.assertEqual(result.status, "Denied")
        self.assertTrue(any("not known" in r for r in result.reasons))

    def test_denied_duplicate_plate_same_zone(self):
        office = PermitOffice()
        first = office.submit(app())
        self.assertEqual(first.status, "Approved")
        second = office.submit(app(driver="Other Driver"))
        self.assertEqual(second.status, "Denied")
        self.assertTrue(any("already has an active permit" in r for r in second.reasons))
        self.assertEqual(len(office.payments), 1)  # only the first ever paid

    def test_same_plate_different_zone_is_allowed(self):
        office = PermitOffice()
        office.submit(app())
        other = office.submit(app(zone="Downtown"))
        self.assertEqual(other.status, "Approved")


class TestExemptFree(unittest.TestCase):
    def test_employee_exempt_zero_fee_no_payment(self):
        office = PermitOffice()
        result = office.submit(app(permit_type="employee"))
        self.assertEqual(result.status, "Approved")
        self.assertEqual(result.fee, 0)
        self.assertIsNone(result.payment)
        self.assertEqual(len(office.payments), 0)
        self.assertTrue(any("$0" in line for line in result.timeline))
        # Asking to pay an exempt permit still creates nothing.
        self.assertIsNone(office.pay(result.application_id))
        self.assertEqual(len(office.payments), 0)


class TestTimelineAndRules(unittest.TestCase):
    def test_timeline_is_plain_words_and_ends_with_status(self):
        office = PermitOffice()
        result = office.submit(app())
        timeline = office.status_timeline(result.application_id)
        self.assertEqual(timeline, result.timeline)
        self.assertTrue(timeline[0].startswith("Applied:"))
        self.assertTrue(timeline[-1].startswith("Status: Approved"))

    def test_denied_timeline_says_no_money_taken(self):
        office = PermitOffice()
        result = office.submit(app(zone="Airport"))
        self.assertTrue(any("No money was taken" in line for line in result.timeline))

    def test_rules_are_demo_rules_in_one_place(self):
        self.assertEqual(RULES["fee_by_type"],
                         {"resident": 30, "visitor": 10, "employee": 0})
        self.assertIn("employee", RULES["exempt_types"])
        self.assertEqual(RULES["plate_min_length"], 4)
        self.assertEqual(RULES["plate_max_length"], 10)


if __name__ == "__main__":
    unittest.main()
