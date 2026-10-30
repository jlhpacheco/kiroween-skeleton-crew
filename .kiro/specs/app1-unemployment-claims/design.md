# Design — App 1: Unemployment Claims

Corresponds to: `specs/app1-unemployment-claims/requirements.md`
Real code (Track B, 2026-10-30): `wba.py`, `base_period.py`,
`claim_flow.py`, `demo.py`; tests in `tests/test_app1.py` (25 tests).

## Overview

Three small modules, each holding one kind of rule, plus a CLI demo.
Money is handled in integer cents or `Decimal` so table edges are
exact. Standard library only.

```
form values (claim date, wages by quarter)
        │
        ▼
base_period.py ──► standard / alternate 4 quarters, highest quarter
        │
        ▼
wba.py ──────────► monetarily_qualifies()?  weekly_benefit_amount()
        │
        ▼
claim_flow.py ───► Claim: Filed → WaitingWeek → Certified → Paid …
        │            waiting week $0 · pay once per week · caps enforced
        ▼
timeline (plain words, numbered) — Claim.render_timeline()
```

## Skeleton reuse (Track A, `skeleton.py`)

The 5 bones and where App 1 follows them:

| Bone | Skeleton (Track A) | App 1 (Track B) — the truth |
|---|---|---|
| 1. Form in | `Intake.submit()` → `Record` with ID | **Imported and used.** `Claim` builds a skeleton `Case` with the form `{claimant, wba}`; the engine's Intake assigns the record ID. |
| 2. Rules check | One `RulesCheck` callable → `RulesResult` | `claim_rules()` in `claim_flow.py` is the callable the engine runs; it carries the verdict of the app-specific rule functions `monetarily_qualifies()` + `weekly_benefit_amount()` in `wba.py` only. |
| 3. Steps move | `StepMachine`, forward-only, logged | The engine's StepMachine, steps `Filed → WaitingWeek → Certified → Paid`; `Claim.state` reads the machine; waiting-week and order guards raise `ClaimError`. |
| 4. Money moves | `MoneyMove.pay()`, key `record:period`, `DoublePayBlocked` | The engine's ledger: every paid week pays through `Case.pay(period="week-N")`; `claim_flow.DoublePayBlocked` IS the skeleton's class (imported, not redefined). The app `payments` dict is the per-week view on top. |
| 5. Timeline | `Timeline` class, plain words | The engine's `Timeline`; `Claim.timeline` reads its entries as plain strings; `render_timeline()` numbers the lines. |

Design rule that follows from this table: since the Oct 30 refactor
(tasks.md B-7, DONE), App 1 literally runs on `skeleton.py` — repo
text may say "built on the skeleton code," and
`app1_unemployment/tests/test_shared_skeleton.py` is the proof that
must keep passing for that sentence to stay.

## Components

### `wba.py` — the §1280 module

- `_TABLE`: published step brackets `(low_cents, high_cents, wba)` for
  highest-quarter wages $900.00–$1,832.99 → WBA $40–$70.
  `TABLE_TOP_CENTS = 183299`.
- `weekly_benefit_amount(highest_quarter_wages) -> int` (whole dollars):
  below $900 → 0; in table → bracket value; above table →
  `ceil(highest_quarter / 26)`, then clamp to $40–$450.
- `monetarily_qualifies(highest_quarter_wages, total_base_period_wages) -> bool`:
  Branch A `hq >= 1300`; Branch B `hq >= 900 and total >= 1.25 * hq`.
- `max_benefit_amount(wba) -> int`: `26 * wba` ($11,700 at the cap).
- Docstring source note (kept verbatim in code): "Clean-room
  implementation from the PUBLIC statute table and formula. No EDD
  source code is used, needed, or wanted."

### `base_period.py` — which four quarters

- Quarter = `(year, quarter_number 1–4)`.
- `standard_base_period(claim)` / `alternate_base_period(claim)`:
  claim may be a `datetime.date` or a `(year, month)` tuple; both
  return `{"quarters": [...4...], "start": date, "end": date}`.
- Standard ends: Jan–Mar claim → Sep 30 prior year; Apr–Jun → Dec 31
  prior year; Jul–Sep → Mar 31 claim year; Oct–Dec → Jun 30 claim year.
- Alternate ends one quarter later in each case: Dec 31 prior year /
  Mar 31 / Jun 30 / Sep 30 respectively.
- `highest_quarter(wages_by_quarter) -> float` (0.0 if empty).

### `claim_flow.py` — the moving claim

- `Claim` dataclass: `claimant`, `wba`, `state`, 
  `waiting_week_certified`, `weeks_paid`, `total_paid`,
  `payments: dict[int, Payment]`, `timeline: list[str]`,
  `max_total = 26 * wba` set in `__post_init__`.
- `certify_waiting_week() -> Decimal(0)`: only from state `Filed`;
  records `Payment(week=0, amount=0)`; ends in state `Certified`;
  appends the waiting-week line + "certify every two weeks" next line.
- `certify_and_pay(week, earnings=0) -> Payment`: guards in order —
  waiting week certified; week in 1–26; week not already paid
  (`DoublePayBlocked`); fewer than 26 weeks paid. Amount =
  `weekly_payment(wba, earnings)`, then capped at the remaining
  balance (`max_total − total_paid`).
- `partial_earnings_deduction(wba, earnings)`: disregard =
  `max($25, 25% of earnings)`; deduction = earnings − disregard,
  clamped 0…WBA. `weekly_payment()` = WBA − deduction.
- `balance` property = `max_total − total_paid`.
- Errors: `ClaimError` (out-of-order / invalid action),
  `DoublePayBlocked` (week paid twice). Both are real exceptions in
  code, not UI messages — there is no UI.

### `demo.py` — the proof run

November 2, 2026 claim; wages `[3200, 4100, 5200, 4800]`; highest
quarter $5,200 → qualifies → WBA $200 → max $5,200. Then: waiting week
$0, week 1 pays $200, week 2 with $200 earnings pays $50, week 3 pays
$200. Total paid $450. This is the demo the submission shows.

## Data model

In memory only. No files, no database, no saved claims between runs.
A `Claim` object *is* the record. (SCDB is the real EDD record book;
this app models its claim/payment logic only and stores nothing.)

## Error handling

| Condition | Real behaviour in code |
|---|---|
| Negative wages / earnings | `ValueError` |
| Paid week before waiting week | `ClaimError` |
| Waiting week certified twice | `ClaimError` |
| Week outside 1–26, or 27th paid week | `ClaimError` |
| Same week paid twice | `DoublePayBlocked`, no money moves |
| Highest quarter below $900 | WBA 0; qualification False; demo timeline stops with "does not qualify" |

## Testing

`tests/test_app1.py` — 25 tests, all passing 2026-10-30: §1280 table
edges ($900 → $40, $1,832.99 → $70, above-table ÷26 rounding, $450
cap), both qualification branches and the below-$900 failure, standard
and alternate windows by claim month, waiting-week order and $0,
double-pay block, partial-earnings disregard (both arms of
greater-of), 26-week and $11,700-at-cap limits, timeline contents.
