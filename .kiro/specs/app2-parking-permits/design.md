# Design — App 2: Parking Permits

Corresponds to: `specs/app2-parking-permits/requirements.md`
Real code (Track C, 2026-10-30): `parking.py`, `demo.py`;
tests in `tests/test_parking.py` (13 tests).

## Overview

One file, `parking.py`, holds the whole app: the demo rules, the form
shape, the office that checks / decides / pays, and the timeline.
It is the skeleton's override layer — new form, new rules, new step
labels; the 5-step shape is unchanged.

```
PermitApplication (driver, plate, address, zone, permit_type)
        │
        ▼
PermitOffice.check_rules() ──► list of plain-words reasons (empty = pass)
        │                              reads RULES — and only RULES
        ▼
steps: Applied → Checked → Approved ──► pay() once (or $0: no payment)
                       └────► Denied ──► fee $0, no money taken
        │
        ▼
PermitResult.timeline — plain words via status_timeline(app_id)
```

## The rules — one place, labelled DEMO

`RULES` dict in `parking.py`, verbatim in substance:

| Key | Value (DEMO) |
|---|---|
| `allowed_zones` | `("North Lot", "Downtown", "Campus West")` |
| `fee_by_type` | `resident: 30, visitor: 10, employee: 0` (whole dollars) |
| `exempt_types` | `("employee",)` |
| `plate_min_length` / `plate_max_length` | 4 / 10 |
| `plate_pattern` | `^[A-Z0-9]+$` (after cleaning) |
| `one_active_per_plate_per_zone` | `True` |

The header comment in `parking.py` is part of the design and must
survive any copy: "These are DEMO rules for this hackathon build.
They are NOT a real city's law, fee schedule, or ordinance."

## Components

- `clean_plate(raw) -> str` — upper-case; strip spaces and hyphens.
- `PermitApplication` dataclass — the Step 1 form (5 fields).
- `Payment` dataclass — `payment_id`, `application_id`, `amount`
  (whole dollars), `kind` — always `"demo-payment"`.
- `PermitResult` dataclass — `application_id`, `status`
  (`Approved` | `Denied`), `fee`, `reasons`, `steps`, `timeline`,
  `payment` (or `None`).
- `PermitOffice` — all state, in memory only:
  - `_next_number` — application counter (`APP-001`, …).
  - `_active: dict[(plate, zone) -> app_id]` — enforces one active
    permit per plate per zone.
  - `_payments: dict[app_id -> Payment]` — the demo ledger.
  - `_results: dict[app_id -> PermitResult]`.
  - `check_rules(app) -> list[str]` — Step 2; reasons in a fixed
    order: driver, address, zone, type, plate length, plate pattern,
    duplicate active permit.
  - `submit(app) -> PermitResult` — Steps 1–3 + 5, and Step 4 inline:
    on approval with a fee over $0 it calls `self.pay(app_id)`.
  - `pay(application_id)` — Step 4 standing alone: repeat call
    returns the stored `Payment`; unknown / denied / $0-exempt
    returns `None` and creates nothing.
  - `status_timeline(application_id) -> list[str]` — Step 5.
- `STEPS = ("Applied", "Checked", "Approved", "Denied")` — note the
  honest shape: `Denied` is a terminal branch off `Checked`, not a
  step after `Approved`. A result's `steps` list is the path taken,
  e.g. `["Applied", "Checked", "Denied"]`.

## Skeleton mapping (code reuse — parking runs on the engine)

Since the Oct 30 refactor (tasks.md C-8, DONE), `parking.py` imports
`skeleton/skeleton.py` and runs every application as a skeleton
`Case` on the office's one shared `MoneyMove` ledger:

| Bone | How parking.py does it now |
|---|---|
| 1. Form in | `PermitApplication` fields become the `Case` form dict; the engine's Intake makes the record (the office keeps its public `APP-NNN` numbers) |
| 2. Rules check | `check_rules()` reading the single `RULES` dict, wrapped as the engine's one `RulesCheck` callable → `RulesResult` |
| 3. Steps move | The engine's `StepMachine` via the `Case`; the result's `steps` list IS `case.step_labels()`: Applied → Checked → Approved/Denied |
| 4. Money moves | `pay()` — idempotent app view over `Case.pay(period="permit-fee")`; the shared engine ledger blocks any second pay |
| 5. Timeline | The engine's `Timeline`; the result's `timeline` reads its entries; `status_timeline()` returns it |

The module docstring now says parking RUNS ON the shared engine.
Proof: `app2_parking/tests/test_shared_skeleton.py` (4 tests —
shared ledger, engine double-pay block, pay-spy counts exactly one
engine pay across the three demo-style cases).

## Demo (`demo.py`) — the three proven cases

1. Ana Ruiz, plate `8XYZ123`, North Lot, resident → Approved, $30,
   one payment `PAY-APP-001`.
2. Ben Cole, plate `4ABC99`, zone `Airport` → Denied (zone not
   allowed), fee $0, no payment.
3. Cy Park, plate `7EMP001`, Downtown, employee → Approved, $0 exempt,
   no payment created.
End state: exactly **1** payment in the ledger. Demo names are
fictional demo data in the code, not real people.

## Error handling

There are no exceptions in the permit flow by design: bad input is a
denial with plain-words reasons, not a crash. The only soft failure is
an unknown ID in `status_timeline()` / `pay()`, handled above.

## Testing

`tests/test_parking.py` — 13 tests, all passing 2026-10-30: each
denial reason, plate cleaning, approval paths for all three types,
fee amounts, double-`pay()` returning the same payment, exempt and
denied creating no payment, duplicate plate+zone blocked, timeline
and steps contents, ledger count after the 3 demo-style cases.
