# Spec — Skeleton Core (the 5 steps)

## Purpose
One lean template that runs every app in this repo.
**Form in → rules check → steps move → money moves → person sees a clear timeline.**

## Requirements
1. **Form in.** A plain dict comes in. It gets its own ID and is copied, so later edits cannot change the saved record. (Code: `Intake.submit()` → `Record` in `skeleton/skeleton.py`.)
2. **Rules check.** ONE callable decides qualify yes/no + amount + a plain-words reason. All domain rules live in that one callable, nowhere else. (Code: `RulesCheck` / `run_rules()`.)
3. **Steps move.** Steps are ordered, forward-only, one at a time. Every move is logged; history is append-only so no case can get lost. (Code: `StepMachine`.)
4. **Money moves.** Pay once per record per period. A second payment for the same record and period is blocked — never pay twice. (Code: `MoneyMove.pay()`.)
5. **Timeline.** A plain-language list: what happened, then what happens next. No jargon. (Code: `Timeline`.)

Glue: `run_case(form, rules_check, steps, period)` runs all 5 steps in order.

## The engine — `Case`
`Case(form, rules_check, *, intake=None, ledger=None)` is the single
engine both apps run on. Construction runs steps 1–2 (Intake, then
the rules callable through `run_rules`). The app then drives:
`start_steps(labels)` (once; choose the path after the rules result
if it branches), `advance()`, `pay(period, amount_cents)`,
`has_paid(period)`, `payments()`, `total_paid_cents()`,
`say(text)` / `say_next(text)`, `step_labels()`. `run_case` itself
is implemented on top of `Case`.

## Building a new app on this skeleton (override layer only)
1. New form fields (a different dict).
2. New rules (a different `RulesCheck` function).
3. New step labels and timeline words.
4. Do NOT change `Intake`, `StepMachine`, `MoneyMove`, or `Timeline`.

Both shipped apps are built exactly this way (refactor, Oct 30):
App 1's `Claim` holds a `Case` with steps Filed → WaitingWeek →
Certified → Paid and pays each week through `Case.pay`; App 2's
`PermitOffice` runs every application as a `Case` on one shared
ledger. Each app's `tests/test_shared_skeleton.py` proves the
sharing (isinstance, pay-spy, engine-level double-pay block).

## Acceptance
- `skeleton/test_skeleton.py` passes (10 tests).
- A double payment for the same period raises/blocks and is covered by a test.
