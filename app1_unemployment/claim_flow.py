"""Claim flow — Filed -> WaitingWeek -> Certified -> Paid.

Clean-room from public California UI rules:
- Waiting week: the first week of a claim is served unpaid, but the
  claimant MUST certify for it. No money moves that week.
- Certification is biweekly in real life; this model certifies and
  pays one week at a time inside each certification, so a payment is
  made at most ONCE per week (idempotent — a second pay attempt for
  the same week is blocked and moves no money).
- Partial earnings: the greater of $25 or 25% of the week's earnings
  is disregarded; the rest is deducted dollar-for-dollar from the WBA.
  A week never pays less than $0.
- Duration: at most 26 payable weeks; total paid can never exceed
  26 x WBA (at the $450 cap, $11,700).

This module is an OVERRIDE LAYER on the shared skeleton engine
(skeleton/skeleton.py). The Claim builds ONE skeleton Case — Intake,
the claim_rules callable, StepMachine, the MoneyMove ledger, and the
Timeline all come from the skeleton. This file supplies only the
claim's form fields, its rules callable, its step labels, and its
words. Benefit math lives in wba.py / base_period.py, unchanged.

The flow emits a plain-language timeline: every step, in order.
Stdlib only.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skeleton"))

from skeleton import Case, DoublePayBlocked, RulesResult  # noqa: E402
from wba import max_benefit_amount  # noqa: E402

__all__ = [
    "MAX_WEEKS",
    "Claim",
    "ClaimError",
    "DoublePayBlocked",
    "Payment",
    "claim_rules",
    "partial_earnings_deduction",
    "weekly_payment",
]

MAX_WEEKS = 26

# The claim's step labels — the only steps this app defines.
CLAIM_STEPS = ["Filed", "WaitingWeek", "Certified", "Paid"]


class ClaimError(Exception):
    """Out-of-order or invalid claim action."""


def claim_rules(record) -> RulesResult:
    """The claim's ONE rules callable, run by the skeleton engine.

    Monetary qualification and the WBA are computed by wba.py before a
    Claim exists; this callable carries that verdict into the engine:
    a claim with a positive WBA qualifies, at that weekly amount.
    """
    wba = record.get("wba", 0)
    if not wba or int(wba) <= 0:
        return RulesResult(False, 0, "No weekly benefit amount")
    return RulesResult(
        True,
        int(wba) * 100,
        "Weekly benefit amount set from base-period wages (CUIC 1280)",
    )


def partial_earnings_deduction(wba: int, earnings) -> Decimal:
    """Deduction from the WBA for a week with part-time earnings.

    Disregard = greater of $25 or 25% of earnings; the remainder is
    deducted dollar-for-dollar. Never below $0, never above the WBA.
    """
    e = Decimal(str(earnings))
    if e < 0:
        raise ValueError("earnings must not be negative")
    disregard = max(Decimal("25"), e * Decimal("0.25"))
    deduction = e - disregard
    if deduction < 0:
        deduction = Decimal("0")
    return min(deduction, Decimal(wba))


def weekly_payment(wba: int, earnings=0) -> Decimal:
    """Amount payable for one payable week (before balance caps)."""
    return Decimal(wba) - partial_earnings_deduction(wba, earnings)


@dataclass
class Payment:
    week: int
    amount: Decimal
    earnings: Decimal = Decimal("0")


class Claim:
    """One unemployment claim, running on the skeleton engine.

    Public API (unchanged by the refactor): claimant, wba, state,
    waiting_week_certified, weeks_paid, total_paid, payments,
    max_total, balance, timeline, certify_waiting_week(),
    certify_and_pay(), render_timeline(). The engine Case is exposed
    as .case so the shared machinery is inspectable, not hidden.
    """

    def __init__(self, claimant: str, wba: int):
        if wba <= 0:
            raise ValueError("claim needs a positive WBA")
        self.claimant = claimant
        self.wba = wba
        # Steps 1-2 on the engine: form in, rules check.
        self.case = Case({"claimant": claimant, "wba": wba}, claim_rules)
        self.case.start_steps(CLAIM_STEPS)
        self.waiting_week_certified = False
        self.weeks_paid = 0
        self.total_paid = Decimal("0")
        self.payments: Dict[int, Payment] = {}
        self.max_total = Decimal(max_benefit_amount(self.wba))
        self.case.say(
            f"Claim filed for {self.claimant}. Weekly benefit: ${self.wba}."
        )
        self.case.say(
            "Next: certify for the waiting week. It must be certified, "
            "but it is not paid."
        )

    # -- engine-backed views ---------------------------------------------
    @property
    def state(self) -> str:
        return self.case.current_step

    @property
    def timeline(self) -> List[str]:
        return [e.text for e in self.case.timeline.entries]

    @property
    def balance(self) -> Decimal:
        return self.max_total - self.total_paid

    # -- waiting week ------------------------------------------------------
    def certify_waiting_week(self) -> Decimal:
        """Serve and certify the unpaid waiting week. Pays $0."""
        if self.waiting_week_certified:
            raise ClaimError("waiting week already certified")
        if self.state != "Filed":
            raise ClaimError(f"cannot serve waiting week from state {self.state}")
        self.case.advance()  # Filed -> WaitingWeek
        self.waiting_week_certified = True
        self.payments[0] = Payment(week=0, amount=Decimal("0"))
        self.case.advance()  # WaitingWeek -> Certified
        self.case.say("Waiting week certified. Payment: $0 (unpaid week).")
        self.case.say("Next: certify every two weeks to keep payments going.")
        return Decimal("0")

    # -- payable weeks -------------------------------------------------------
    def certify_and_pay(self, week: int, earnings=0) -> Payment:
        """Certify one payable week (1-26) and pay it — once only.

        A second call for the same week raises DoublePayBlocked (the
        skeleton's own exception class) and moves no money. Money for
        every paid week moves through the skeleton's MoneyMove ledger,
        keyed one payment per week.
        """
        if not self.waiting_week_certified:
            raise ClaimError("waiting week must be certified before any paid week")
        if week < 1 or week > MAX_WEEKS:
            raise ClaimError(f"week must be 1-{MAX_WEEKS}")
        if week in self.payments:
            raise DoublePayBlocked(f"week {week} already paid — no second payment")
        if self.weeks_paid >= MAX_WEEKS:
            raise ClaimError("all 26 weeks used")
        amount = weekly_payment(self.wba, earnings)
        # Balance cap: never pay past 26 x WBA in total.
        remaining = self.max_total - self.total_paid
        if amount > remaining:
            amount = remaining
        if amount > 0:
            cents = int((amount * 100).to_integral_value(rounding=ROUND_HALF_UP))
            if cents > 0:
                self.case.pay(period=f"week-{week}", amount_cents=cents)
        payment = Payment(week=week, amount=amount, earnings=Decimal(str(earnings)))
        self.payments[week] = payment
        self.weeks_paid += 1
        self.total_paid += amount
        if self.state != "Paid":
            self.case.advance()  # Certified -> Paid
        e = Decimal(str(earnings))
        if e > 0:
            self.case.say(
                f"Week {week} certified. Earnings ${e:.2f} reported; "
                f"payment: ${amount:.2f}."
            )
        else:
            self.case.say(f"Week {week} certified. Payment: ${amount:.2f}.")
        if self.weeks_paid >= MAX_WEEKS or self.total_paid >= self.max_total:
            self.case.say("Benefit year amount used up. Claim complete.")
        return payment

    def render_timeline(self) -> str:
        return "\n".join(f"{i+1}. {line}" for i, line in enumerate(self.timeline))
