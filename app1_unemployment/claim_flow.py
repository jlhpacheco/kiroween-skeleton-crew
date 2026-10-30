"""Claim flow — Filed -> WaitingWeek -> Certified (biweekly) -> Paid.

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

The flow emits a plain-language timeline: every step, in order.
Stdlib only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional

from wba import max_benefit_amount

MAX_WEEKS = 26


class DoublePayBlocked(Exception):
    """A week was paid (or attempted) more than once."""


class ClaimError(Exception):
    """Out-of-order or invalid claim action."""


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


@dataclass
class Claim:
    claimant: str
    wba: int
    state: str = "Filed"  # Filed -> WaitingWeek -> Certified -> Paid ...
    waiting_week_certified: bool = False
    weeks_paid: int = 0
    total_paid: Decimal = Decimal("0")
    payments: Dict[int, Payment] = field(default_factory=dict)
    timeline: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.wba <= 0:
            raise ValueError("claim needs a positive WBA")
        self.max_total = Decimal(max_benefit_amount(self.wba))
        self.timeline.append(
            f"Claim filed for {self.claimant}. Weekly benefit: ${self.wba}."
        )
        self.timeline.append(
            "Next: certify for the waiting week. It must be certified, "
            "but it is not paid."
        )

    # -- waiting week ---------------------------------------------------
    def certify_waiting_week(self) -> Decimal:
        """Serve and certify the unpaid waiting week. Pays $0."""
        if self.waiting_week_certified:
            raise ClaimError("waiting week already certified")
        if self.state != "Filed":
            raise ClaimError(f"cannot serve waiting week from state {self.state}")
        self.state = "WaitingWeek"
        self.waiting_week_certified = True
        self.payments[0] = Payment(week=0, amount=Decimal("0"))
        self.state = "Certified"
        self.timeline.append("Waiting week certified. Payment: $0 (unpaid week).")
        self.timeline.append("Next: certify every two weeks to keep payments going.")
        return Decimal("0")

    # -- payable weeks ----------------------------------------------------
    def certify_and_pay(self, week: int, earnings=0) -> Payment:
        """Certify one payable week (1-26) and pay it — once only.

        A second call for the same week raises DoublePayBlocked and
        moves no money (idempotent payment, one payment per week).
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
        payment = Payment(week=week, amount=amount, earnings=Decimal(str(earnings)))
        self.payments[week] = payment
        self.weeks_paid += 1
        self.total_paid += amount
        self.state = "Paid"
        e = Decimal(str(earnings))
        if e > 0:
            self.timeline.append(
                f"Week {week} certified. Earnings ${e:.2f} reported; "
                f"payment: ${amount:.2f}."
            )
        else:
            self.timeline.append(f"Week {week} certified. Payment: ${amount:.2f}.")
        if self.weeks_paid >= MAX_WEEKS or self.total_paid >= self.max_total:
            self.timeline.append("Benefit year amount used up. Claim complete.")
        return payment

    @property
    def balance(self) -> Decimal:
        return self.max_total - self.total_paid

    def render_timeline(self) -> str:
        return "\n".join(f"{i+1}. {line}" for i, line in enumerate(self.timeline))
