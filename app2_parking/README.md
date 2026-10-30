# App 2 — Parking Permits (Kiroween 2026, Skeleton Crew)

**One skeleton, two different worlds.** The same 5 steps that run App 1
(the California unemployment claims modernizer) also run this app.
Only the form, the rules, and the labels change.

> **New build note:** This is a NEW Kiroween build, made inside the
> Oct 30, 2026 submission window. It reuses the skeleton *idea* only.
> No code is copied from any prior parking app — Duvara and Solvia
> were not copied, read, or modified for this build.

## The skeleton, side by side

| Step | Skeleton (one sentence) | App 1 — Unemployment claims | App 2 — Parking permits (this app) |
|---|---|---|---|
| 1. Form in | A person fills in a form | Claim form: who you are, where you worked, what you earned | Permit application: driver, car plate, address, permit type |
| 2. Rules check | Clear rules say yes or no | Public benefit rules (wage table, base period, waiting week) | Car / address allowed? Plate fits, zone is allowed, no duplicate |
| 3. Steps move | The case moves step by step | Filed → checked → decided | Applied → Checked → Approved (or Denied, with a plain reason) |
| 4. Money moves | Money moves once, the right amount | Benefit amount is set and paid | Driver pays the fee once; exempt ($0) issues free, no payment |
| 5. Timeline | The person sees a clear timeline | Claim status and next steps in plain words | Permit status in plain words |

## Demo rules (NOT a real city's law)

All rules live in **one place** — the `RULES` dict at the top of
`parking.py`. They are demo rules invented for this build:

| Rule | Demo value |
|---|---|
| Allowed zones | North Lot, Downtown, Campus West |
| Plate | 4–10 characters, letters and numbers only |
| Duplicates | One active permit per plate per zone |
| Fee — resident | $30 |
| Fee — visitor | $10 |
| Fee — employee | $0 (exempt — issues free, no payment) |

Money in this demo is a local ledger entry labelled `demo-payment`.
No real payment is taken, and nothing is charged.

## Run it

```bash
python3 demo.py                                  # 3 cases: paid, denied, exempt
python3 -m unittest discover -s tests -v         # the test suite
```

Stdlib only. No installs, no network.

## Files

| File | What it is |
|---|---|
| `parking.py` | The whole override layer: form, rules, steps, money, timeline |
| `demo.py` | Runs the 3 cases and prints each timeline |
| `tests/test_parking.py` | Unittest coverage for every path above |
| `RESULT.md` | Hypothesis, method, metric, verdict for this track |
