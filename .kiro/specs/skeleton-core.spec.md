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

## Building a new app on this skeleton (override layer only)
1. New form fields (a different dict).
2. New rules (a different `RulesCheck` function).
3. New step labels and timeline words.
4. Do NOT change `Intake`, `StepMachine`, `MoneyMove`, or `Timeline`.

## Acceptance
- `skeleton/test_skeleton.py` passes (10 tests).
- A double payment for the same period raises/blocks and is covered by a test.
