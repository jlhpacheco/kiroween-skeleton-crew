"""App 2 — Parking Permits. A small override layer on the 5-step skeleton.

Skeleton (same for both apps):
    1. Form in          -> a person fills in a form
    2. Rules check      -> clear rules say yes or no, with a plain reason
    3. Steps move       -> the case moves step by step
    4. Money moves      -> a fee is paid once (or $0, free)
    5. Timeline         -> the person sees status in plain words

Parking meaning:
    1. Form in          -> permit application (driver, plate, address, type)
    2. Rules check      -> car / address allowed?
    3. Steps move       -> Applied -> Checked -> Approved (or Denied)
    4. Money moves      -> driver pays the fee once; exempt pays $0
    5. Timeline         -> permit status in plain words

NEW Kiroween build, started in the Oct 30, 2026 submission window.
Parking RUNS ON the shared engine in skeleton/skeleton.py — its
Case / StepMachine / MoneyMove / Timeline do the work — and this
module supplies only the form, the rules, and the step labels.
No code is copied from any prior parking app (Duvara / Solvia are
not copied, read, or modified here).

Stdlib only (plus the repo's own skeleton engine). No network, no
files, no real payments — money is a local ledger entry that stands
in for a payment, clearly labelled DEMO.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skeleton"))

from skeleton import Case, MoneyMove, RulesResult  # noqa: E402

# ---------------------------------------------------------------------------
# RULES — defined in ONE place. These are DEMO rules for this hackathon
# build. They are NOT a real city's law, fee schedule, or ordinance.
# ---------------------------------------------------------------------------
RULES = {
    # Demo zones only. An address must be in one of these zones.
    "allowed_zones": ("North Lot", "Downtown", "Campus West"),
    # Fee by permit type, in whole dollars. DEMO fees.
    "fee_by_type": {
        "resident": 30,
        "visitor": 10,
        "employee": 0,  # employee permits are exempt in this demo
    },
    # Types that never pay.
    "exempt_types": ("employee",),
    # Plate: 4-10 characters, letters and numbers only (after cleaning).
    "plate_min_length": 4,
    "plate_max_length": 10,
    "plate_pattern": re.compile(r"^[A-Z0-9]+$"),
    # One active permit per plate per zone.
    "one_active_per_plate_per_zone": True,
}

STEPS = ("Applied", "Checked", "Approved", "Denied")


def clean_plate(raw: str) -> str:
    """Upper-case the plate and drop spaces and hyphens."""
    return re.sub(r"[\s-]", "", (raw or "").upper())


@dataclass
class PermitApplication:
    """Step 1 — the form."""

    driver: str
    plate: str
    address: str
    zone: str
    permit_type: str  # resident | visitor | employee


@dataclass
class Payment:
    payment_id: str
    application_id: str
    amount: int  # dollars
    kind: str  # "demo-payment" (never a real charge)


@dataclass
class PermitResult:
    application_id: str
    status: str  # "Approved" | "Denied"
    fee: int  # dollars owed; 0 for exempt or denied
    reasons: list[str] = field(default_factory=list)  # plain-word denial reasons
    steps: list[str] = field(default_factory=list)  # steps the case went through
    timeline: list[str] = field(default_factory=list)  # plain words for the person
    payment: Payment | None = None


class PermitOffice:
    """Holds state: active permits and the payment ledger (in memory only)."""

    def __init__(self) -> None:
        self._next_number = 1
        self._active: dict[tuple[str, str], str] = {}  # (plate, zone) -> app id
        self._payments: dict[str, Payment] = {}  # application_id -> Payment
        self._results: dict[str, PermitResult] = {}
        # ONE shared skeleton ledger for every case this office runs.
        self._ledger = MoneyMove()
        self._cases: dict[str, Case] = {}  # application_id -> skeleton Case

    # -- Step 2: rules check -------------------------------------------------
    def check_rules(self, app: PermitApplication) -> list[str]:
        """Return a list of plain-word reasons it fails. Empty list = passes."""
        reasons: list[str] = []
        if not (app.driver or "").strip():
            reasons.append("No driver name on the form.")
        if not (app.address or "").strip():
            reasons.append("No address on the form.")
        if app.zone not in RULES["allowed_zones"]:
            reasons.append(
                f"Address is not in an allowed zone. "
                f"Allowed zones: {', '.join(RULES['allowed_zones'])}."
            )
        if app.permit_type not in RULES["fee_by_type"]:
            reasons.append(
                f"Permit type '{app.permit_type}' is not known. "
                f"Types: {', '.join(RULES['fee_by_type'])}."
            )
        plate = clean_plate(app.plate)
        if not (RULES["plate_min_length"] <= len(plate) <= RULES["plate_max_length"]):
            reasons.append(
                f"Plate must be {RULES['plate_min_length']}-"
                f"{RULES['plate_max_length']} characters long."
            )
        elif not RULES["plate_pattern"].match(plate):
            reasons.append("Plate may use letters and numbers only.")
        if RULES["one_active_per_plate_per_zone"] and (plate, app.zone) in self._active:
            reasons.append("This car already has an active permit for this zone.")
        return reasons

    # -- Steps 1-3 + 5: submit, check, decide, timeline ----------------------
    def submit(self, app: PermitApplication) -> PermitResult:
        app_id = f"APP-{self._next_number:03d}"
        self._next_number += 1

        form = {
            "driver": app.driver,
            "plate": app.plate,
            "address": app.address,
            "zone": app.zone,
            "permit_type": app.permit_type,
        }

        # The rules callable the engine runs: this app's check_rules,
        # translated into the skeleton's RulesResult contract.
        stash: dict[str, list[str]] = {}

        def rules_callable(record) -> RulesResult:
            reasons = self.check_rules(app)
            stash["reasons"] = reasons
            if reasons:
                return RulesResult(qualifies=False, amount_cents=0,
                                   reason=reasons[0])
            fee = RULES["fee_by_type"].get(app.permit_type, 0)
            return RulesResult(qualifies=True, amount_cents=fee * 100,
                               reason="All parking rules passed")

        # Steps 1-2 run inside the engine: Intake + rules check.
        case = Case(form, rules_callable, ledger=self._ledger)
        self._cases[app_id] = case
        reasons = stash.get("reasons", [])

        case.say(f"Applied: {app.driver} — {app.permit_type} permit "
                 f"for plate {clean_plate(app.plate)} in {app.zone}.")

        # Step 3: steps move — the path depends on the rules result.
        if case.rules.qualifies:
            case.start_steps(["Applied", "Checked", "Approved"])
        else:
            case.start_steps(["Applied", "Checked", "Denied"])
        case.advance()  # -> Checked
        case.advance()  # -> Approved or Denied

        if not case.rules.qualifies:
            case.say("Checked: the rules say no.")
            for reason in reasons:
                case.say(f"Denied: {reason}")
            case.say("Status: Denied. No money was taken.")
            result = PermitResult(
                app_id, "Denied", fee=0, reasons=reasons,
                steps=case.step_labels(),
                timeline=[e.text for e in case.timeline.entries],
            )
            self._results[app_id] = result
            return result

        fee = case.rules.amount_cents // 100
        case.say("Checked: the rules say yes.")
        case.say(f"Approved: permit is approved. Fee is ${fee}.")
        self._active[(clean_plate(app.plate), app.zone)] = app_id
        result = PermitResult(
            app_id, "Approved", fee=fee,
            steps=case.step_labels(),
            timeline=[e.text for e in case.timeline.entries],
        )
        self._results[app_id] = result

        # -- Step 4: money moves -------------------------------------------
        if fee == 0:
            case.say("Money: $0 — exempt. No payment needed. Permit is free.")
            case.say("Status: Approved and active. You can park.")
        else:
            self.pay(app_id)  # the demo's one payment step
            case.say(f"Money: driver paid ${fee} (demo payment, not a real charge).")
            case.say("Status: Approved, paid, and active. You can park.")
        result.timeline = [e.text for e in case.timeline.entries]
        return result

    # -- Step 4: money moves, once only --------------------------------------
    def pay(self, application_id: str) -> Payment | None:
        """Pay an approved application's fee once.

        Idempotent: calling pay again for the same application returns the
        SAME payment and charges nothing extra. Exempt ($0) applications
        return None — no payment is ever created for them. The shared
        skeleton ledger underneath is the pay-once guard: it raises
        DoublePayBlocked if the same record+period is ever paid twice.
        """
        if application_id in self._payments:
            return self._payments[application_id]
        result = self._results.get(application_id)
        if result is None or result.status != "Approved" or result.fee == 0:
            return None
        case = self._cases.get(application_id)
        if case is None:
            return None
        case.pay(period="permit-fee", amount_cents=result.fee * 100)
        payment = Payment(
            payment_id=f"PAY-{application_id}",
            application_id=application_id,
            amount=result.fee,
            kind="demo-payment",
        )
        self._payments[application_id] = payment
        result.payment = payment
        return payment

    @property
    def payments(self) -> dict[str, Payment]:
        return dict(self._payments)

    def status_timeline(self, application_id: str) -> list[str]:
        """Step 5 — the timeline a person sees, in plain words."""
        result = self._results.get(application_id)
        return list(result.timeline) if result else [f"No application {application_id}."]
