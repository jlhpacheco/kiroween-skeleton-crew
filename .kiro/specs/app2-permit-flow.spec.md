# Spec — App 2: Permit Flow (parking permits)

## Purpose
Prove the same skeleton in a different world. App 2 is an override layer only: new form, new rules, new labels — the 5 steps do not change.
Implemented in `app2_parking/parking.py` (rules in ONE place: the `RULES` dict at the top of the file). Shown by `app2_parking/demo.py` (3 cases).

## Flow
1. **Form in:** permit application — driver, car plate, address, zone, permit type.
2. **Rules check:** plate fits (4–10 characters, letters and numbers only); zone is allowed; no duplicate active permit for the same plate in the same zone.
3. **Steps move:** Applied → Checked → Approved (or Denied, with a plain reason).
4. **Money moves:** the driver pays the fee once, before issue. Exempt ($0) issues free — no payment is created.
5. **Timeline:** permit status in plain words.

## Demo rules (NOT a real city's law — invented for this build, labeled DEMO in the code)
| Rule | Demo value |
|---|---|
| Allowed zones | North Lot, Downtown, Campus West |
| Fee — resident | $30 |
| Fee — visitor | $10 |
| Fee — employee | $0 (exempt) |

Money in this demo is a local ledger entry labeled `demo-payment`. No real payment is taken.

## Clean-room note
New build inside the Oct 30, 2026 submission window. It reuses the skeleton idea only — no code is copied from any prior parking app.

## Acceptance
- `app2_parking/tests/test_parking.py` passes (13 tests): paid case, denied case, exempt case, duplicate blocked, bad plate denied.
- Demo prints 3 cases and exactly 1 ledger payment.
