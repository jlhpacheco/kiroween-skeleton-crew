"""
Skeleton Crew — lean template
One sentence: Form in → rules check → steps move → money moves → person sees a clear timeline.

Pure Python, stdlib only. No dependencies.
Clean-room design from public rules patterns. Domain rules live in ONE place:
the RulesCheck callable you pass in. Swap the rules, keep the skeleton.

Usage pattern:
    record = Intake().submit({"name": "Alex", ...})
    result = my_rules(record)          # RulesCheck
    machine = StepMachine([...])       # ordered steps
    ledger = MoneyMove()
    ledger.pay(record.id, period="2026-W44", amount_cents=...)
    timeline = Timeline(); timeline.add(...)
"""
from __future__ import annotations

import hashlib
import itertools
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 1. Form in — Intake
# ---------------------------------------------------------------------------

_id_counter = itertools.count(1)


@dataclass
class Record:
    id: str
    data: Dict[str, Any]
    created_at: float = field(default_factory=time.time)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


class Intake:
    """Takes a plain dict in, returns a Record with a stable ID. Nothing else."""

    def __init__(self, prefix: str = "REC"):
        self._prefix = prefix
        self._records: Dict[str, Record] = {}

    def submit(self, form: Dict[str, Any]) -> Record:
        if not isinstance(form, dict):
            raise TypeError("form must be a dict")
        if not form:
            raise ValueError("form must not be empty")
        n = next(_id_counter)
        # Deterministic-ish ID: prefix + counter + short hash of sorted items
        digest = hashlib.sha256(repr(sorted(form.items())).encode()).hexdigest()[:6]
        rid = f"{self._prefix}-{n:04d}-{digest}"
        record = Record(id=rid, data=dict(form))  # copy — caller can't mutate later
        self._records[rid] = record
        return record

    def get(self, record_id: str) -> Optional[Record]:
        return self._records.get(record_id)


# ---------------------------------------------------------------------------
# 2. Rules check — ONE place for all domain rules
# ---------------------------------------------------------------------------

@dataclass
class RulesResult:
    qualifies: bool
    amount_cents: int = 0
    reason: str = ""

    def __bool__(self) -> bool:
        return self.qualifies


# A RulesCheck is any callable: Record -> RulesResult
# Example (domain code lives HERE, nowhere else in the skeleton):
#
#   def unemployment_rules(record):
#       wages = record.get("wages_cents", 0)
#       if wages <= 0:
#           return RulesResult(False, 0, "No wages in base period")
#       wba = min(45000, max(4000, wages // 26))  # illustrative public-table shape
#       return RulesResult(True, wba, "Weekly benefit from base-period wages")
#
RulesCheck = Callable[[Record], RulesResult]


def run_rules(check: RulesCheck, record: Record) -> RulesResult:
    """Run the single rules callable. This is the only rules entry point."""
    result = check(record)
    if not isinstance(result, RulesResult):
        raise TypeError("RulesCheck must return RulesResult")
    if result.amount_cents < 0:
        raise ValueError("amount_cents must not be negative")
    if not result.qualifies and result.amount_cents != 0:
        raise ValueError("non-qualifying result must have amount 0")
    return result


# ---------------------------------------------------------------------------
# 3. Steps move — StepMachine
# ---------------------------------------------------------------------------

@dataclass
class StepEvent:
    from_step: Optional[str]
    to_step: str
    at: float
    note: str = ""


class StepMachine:
    """
    Ordered steps. You can only move forward one step at a time,
    or stay. Every transition is logged. State is never lost:
    history is append-only.
    """

    def __init__(self, steps: List[str]):
        if not steps:
            raise ValueError("steps must not be empty")
        if len(set(steps)) != len(steps):
            raise ValueError("steps must be unique")
        self._steps = list(steps)
        self._index = 0
        self._history: List[StepEvent] = [
            StepEvent(from_step=None, to_step=steps[0], at=time.time(), note="started")
        ]

    @property
    def current(self) -> str:
        return self._steps[self._index]

    @property
    def steps(self) -> List[str]:
        return list(self._steps)

    @property
    def history(self) -> List[StepEvent]:
        return list(self._history)

    @property
    def is_done(self) -> bool:
        return self._index == len(self._steps) - 1

    def advance(self, note: str = "") -> str:
        if self.is_done:
            raise RuntimeError(f"already at final step: {self.current}")
        prev = self.current
        self._index += 1
        self._history.append(
            StepEvent(from_step=prev, to_step=self.current, at=time.time(), note=note)
        )
        return self.current

    def next_step(self) -> Optional[str]:
        if self.is_done:
            return None
        return self._steps[self._index + 1]


# ---------------------------------------------------------------------------
# 4. Money moves — MoneyMove (idempotent, pay once per period)
# ---------------------------------------------------------------------------

@dataclass
class Payment:
    record_id: str
    period: str
    amount_cents: int
    idempotency_key: str
    at: float = field(default_factory=time.time)


class DoublePayBlocked(Exception):
    """Raised when the same record+period is paid twice."""


class MoneyMove:
    """
    Pay once per period per record. The idempotency key is
    f"{record_id}:{period}" — a second pay() for the same key
    raises DoublePayBlocked and moves no money.
    """

    def __init__(self):
        self._payments: Dict[str, Payment] = {}  # key -> Payment

    @staticmethod
    def key_for(record_id: str, period: str) -> str:
        return f"{record_id}:{period}"

    def pay(self, record_id: str, period: str, amount_cents: int) -> Payment:
        if amount_cents <= 0:
            raise ValueError("amount_cents must be positive to pay")
        if not period:
            raise ValueError("period is required")
        key = self.key_for(record_id, period)
        if key in self._payments:
            raise DoublePayBlocked(
                f"already paid record {record_id} for period {period} "
                f"(key={key}, amount_cents={self._payments[key].amount_cents})"
            )
        payment = Payment(
            record_id=record_id,
            period=period,
            amount_cents=amount_cents,
            idempotency_key=key,
        )
        self._payments[key] = payment
        return payment

    def has_paid(self, record_id: str, period: str) -> bool:
        return self.key_for(record_id, period) in self._payments

    def payments_for(self, record_id: str) -> List[Payment]:
        return [p for p in self._payments.values() if p.record_id == record_id]

    def total_paid_cents(self, record_id: str) -> int:
        return sum(p.amount_cents for p in self.payments_for(record_id))


# ---------------------------------------------------------------------------
# 5. Person sees a clear timeline — Timeline
# ---------------------------------------------------------------------------

@dataclass
class TimelineEntry:
    text: str
    at: float = field(default_factory=time.time)
    kind: str = "event"  # event | next


class Timeline:
    """Plain-language list: what happened + what's next. No jargon."""

    def __init__(self):
        self._entries: List[TimelineEntry] = []

    def add(self, text: str) -> None:
        self._entries.append(TimelineEntry(text=text, kind="event"))

    def add_next(self, text: str) -> None:
        self._entries.append(TimelineEntry(text=text, kind="next"))

    def lines(self) -> List[str]:
        out = []
        for e in self._entries:
            prefix = "Next: " if e.kind == "next" else "- "
            out.append(f"{prefix}{e.text}")
        return out

    def render(self) -> str:
        return "\n".join(self.lines())

    @property
    def entries(self) -> List[TimelineEntry]:
        return list(self._entries)


# ---------------------------------------------------------------------------
# Glue — run one record through all five steps
# ---------------------------------------------------------------------------

@dataclass
class CaseResult:
    record: Record
    rules: RulesResult
    machine: StepMachine
    payments: List[Payment]
    timeline: Timeline


def run_case(
    form: Dict[str, Any],
    rules_check: RulesCheck,
    steps: List[str],
    period: str,
    *,
    intake: Optional[Intake] = None,
    ledger: Optional[MoneyMove] = None,
) -> CaseResult:
    """
    The whole skeleton in one function:
    1 form in, 2 rules check, 3 steps move, 4 money moves (if qualifies),
    5 timeline built in plain language.
    """
    intake = intake or Intake()
    ledger = ledger or MoneyMove()
    timeline = Timeline()

    record = intake.submit(form)
    timeline.add(f"You submitted your form. Your reference is {record.id}.")

    result = run_rules(rules_check, record)
    machine = StepMachine(steps)

    payments: List[Payment] = []
    if result.qualifies:
        timeline.add(f"We checked the rules: you qualify. Amount: ${result.amount_cents / 100:.2f}.")
        if result.reason:
            timeline.add(f"Why: {result.reason}")
        # Walk all steps except we stop before final, then complete on pay
        while not machine.is_done:
            nxt = machine.next_step()
            machine.advance()
            if machine.is_done:
                break
            timeline.add(f"Step done: {machine.current}.")
        payment = ledger.pay(record.id, period=period, amount_cents=result.amount_cents)
        payments.append(payment)
        timeline.add(f"Payment sent for {period}: ${payment.amount_cents / 100:.2f}.")
        timeline.add_next("Certify again next period to keep payments going.")
    else:
        timeline.add(f"We checked the rules: you do not qualify right now.")
        if result.reason:
            timeline.add(f"Why: {result.reason}")
        # Move one step to a clear end state label if present, else stay
        timeline.add_next("Check the reason above. You can submit a new form if your facts change.")

    return CaseResult(
        record=record, rules=result, machine=machine, payments=payments, timeline=timeline
    )
