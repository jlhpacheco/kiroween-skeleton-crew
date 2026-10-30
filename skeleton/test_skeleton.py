"""Tests for the Skeleton Crew template. Stdlib unittest only."""
import unittest

from skeleton import (
    DoublePayBlocked,
    Intake,
    MoneyMove,
    RulesResult,
    StepMachine,
    Timeline,
    run_case,
    run_rules,
)


# Domain rules live in ONE place in these tests too — this single function.
def demo_rules(record):
    wages = record.get("wages_cents", 0)
    if wages <= 0:
        return RulesResult(False, 0, "No wages in base period")
    # Illustrative shape only (public-table style): clamp $40-$450/week
    wba = max(4000, min(45000, wages // 26))
    return RulesResult(True, wba, "Weekly benefit from base-period wages")


STEPS = ["applied", "checked", "approved", "paid"]


class TestHappyPath(unittest.TestCase):
    def test_full_case_qualifies_and_pays(self):
        result = run_case(
            {"name": "Alex", "wages_cents": 520000},
            demo_rules, STEPS, period="2026-W44",
        )
        self.assertTrue(result.rules.qualifies)
        self.assertEqual(result.rules.amount_cents, 20000)  # 520000//26
        self.assertEqual(len(result.payments), 1)
        self.assertEqual(result.payments[0].amount_cents, 20000)
        self.assertTrue(result.machine.is_done)
        self.assertEqual(result.machine.current, "paid")
        text = result.timeline.render()
        self.assertIn("you qualify", text)
        self.assertIn("Payment sent", text)
        self.assertIn("Next:", text)

    def test_intake_gives_id_and_copies_form(self):
        intake = Intake()
        form = {"name": "Sam"}
        rec = intake.submit(form)
        self.assertTrue(rec.id.startswith("REC-"))
        form["name"] = "Changed"
        self.assertEqual(rec.data["name"], "Sam")

    def test_steps_logged_in_order(self):
        m = StepMachine(STEPS)
        m.advance(); m.advance(); m.advance()
        tos = [e.to_step for e in m.history]
        self.assertEqual(tos, STEPS)
        with self.assertRaises(RuntimeError):
            m.advance()

    def test_not_qualify_no_payment(self):
        result = run_case({"name": "Jo", "wages_cents": 0}, demo_rules, STEPS, period="2026-W44")
        self.assertFalse(result.rules.qualifies)
        self.assertEqual(result.payments, [])
        self.assertIn("do not qualify", result.timeline.render())


class TestDoublePayBlocked(unittest.TestCase):
    def test_second_pay_same_period_blocked(self):
        ledger = MoneyMove()
        ledger.pay("REC-1", "2026-W44", 20000)
        with self.assertRaises(DoublePayBlocked):
            ledger.pay("REC-1", "2026-W44", 20000)
        self.assertEqual(ledger.total_paid_cents("REC-1"), 20000)

    def test_different_period_pays(self):
        ledger = MoneyMove()
        ledger.pay("REC-1", "2026-W44", 20000)
        ledger.pay("REC-1", "2026-W46", 20000)
        self.assertEqual(ledger.total_paid_cents("REC-1"), 40000)
        self.assertTrue(ledger.has_paid("REC-1", "2026-W46"))

    def test_run_case_twice_same_ledger_blocked(self):
        ledger = MoneyMove()
        intake = Intake()
        r1 = run_case({"name": "Alex", "wages_cents": 520000}, demo_rules, STEPS,
                      period="2026-W44", intake=intake, ledger=ledger)
        # Same record id + period via direct ledger call must block
        with self.assertRaises(DoublePayBlocked):
            ledger.pay(r1.record.id, "2026-W44", 20000)


class TestRulesInOnePlace(unittest.TestCase):
    def test_swapping_rules_changes_outcome_without_touching_skeleton(self):
        # Same form, same skeleton — only the rules callable changes.
        form = {"name": "Alex", "wages_cents": 520000}
        yes = run_case(form, demo_rules, STEPS, period="2026-W44")
        self.assertTrue(yes.rules.qualifies)

        def deny_all(record):
            return RulesResult(False, 0, "Swapped rules: paused")

        no = run_case(form, deny_all, STEPS, period="2026-W44")
        self.assertFalse(no.rules.qualifies)
        self.assertEqual(no.payments, [])

    def test_rules_result_contract_enforced(self):
        def bad(record):
            return RulesResult(False, 500, "should be zero when not qualifying")
        with self.assertRaises(ValueError):
            run_rules(bad, Intake().submit({"x": 1}))

    def test_timeline_plain_lines(self):
        t = Timeline()
        t.add("You submitted your form.")
        t.add_next("Wait for the check.")
        self.assertEqual(t.lines(), ["- You submitted your form.", "Next: Wait for the check."])


if __name__ == "__main__":
    unittest.main()
