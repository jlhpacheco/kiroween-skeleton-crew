# Skeleton Crew — Template

One sentence:

**Form in → rules check → steps move → money moves → person sees a clear timeline.**

Swap the form and the rules. Keep the skeleton. That is how one skeleton
becomes two different apps (unemployment claims, parking permits, …).

Pure Python, standard library only. No pip installs, no network, no database.

## The 5 steps

| # | Step | What it does | Code |
|---|------|--------------|------|
| 1 | **Form in** | A plain dict comes in. It gets an ID and is copied, so later edits can't change it. | `Intake.submit()` → `Record` |
| 2 | **Rules check** | ONE callable decides: qualify yes/no + amount + plain reason. **All domain rules live here, in one place, nowhere else.** | `RulesCheck` / `run_rules()` |
| 3 | **Steps move** | Ordered steps, forward only, one at a time. Every move is logged. History is append-only — no lost state. | `StepMachine` |
| 4 | **Money moves** | Pay once per record per period. A second pay for the same period is blocked — never double-pay. | `MoneyMove.pay()` |
| 5 | **Clear timeline** | Plain-language list: what happened, then what's next. No jargon. | `Timeline` |

Glue: `run_case(form, rules_check, steps, period)` runs all 5 in order.

## Run it

```bash
python3 -m unittest test_skeleton -v   # run the tests
```

```python
from skeleton import run_case, RulesResult

def my_rules(record):          # <-- your domain rules, this one function only
    ...
    return RulesResult(True, amount_cents, "reason in plain words")

result = run_case({"name": "Alex", ...}, my_rules,
                  steps=["applied", "checked", "approved", "paid"],
                  period="2026-W44")
print(result.timeline.render())
```

## Build a new app on it (override layer only)

1. New form fields (just a different dict).
2. New rules (just a different `RulesCheck` function).
3. New step labels + timeline words.
4. Do **not** change Intake, StepMachine, MoneyMove, or Timeline.

## Clean-room note

Built from public rule patterns only. No copied source code from any
government system. Domain amounts in tests are illustrative shapes,
not a legal determination — the real app's rules function must cite
its public source (statute / published table) in its own docstring.
