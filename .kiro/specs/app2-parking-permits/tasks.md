# Tasks — App 2: Parking Permits

Corresponds to: `specs/app2-parking-permits/requirements.md` and
`design.md`. `[x]` = built and test-proven in Track C (2026-10-30);
`[ ]` = not built.

## Built and proven (Track C, 13/13 tests)

- [x] C-1. `RULES` dict in `parking.py` — demo zones, demo fees
  (resident $30 / visitor $10 / employee $0), exempt types, plate
  rules, one-active-per-plate-per-zone. Labelled DEMO in the code
  header. (Req. 2)
- [x] C-2. `PermitApplication` form + sequential IDs `APP-001`, …
  (Req. 1)
- [x] C-3. `PermitOffice.check_rules()` — plain-words reason per
  failure; empty list = pass; `clean_plate()` normalisation. (Req. 2)
- [x] C-4. Steps recorded per case: Applied → Checked → Approved or
  Denied. (Req. 3)
- [x] C-5. `pay()` — one demo payment per approved non-exempt
  application; repeat call returns the same payment; exempt and
  denied create none. (Req. 4)
- [x] C-6. Plain-language timeline per application +
  `status_timeline()`; unknown ID gets a plain "No application" line.
  (Req. 5)
- [x] C-7. `demo.py` — 3 cases (approved+paid, denied, exempt free);
  ledger ends with exactly 1 payment. README with the side-by-side
  App 1 / App 2 skeleton table.

## Not built — next tasks, in order

- [ ] C-8. Decide the reuse question, same as App 1's B-7: either run
  parking on `skeleton.py`'s actual classes, or keep the permanent
  wording "reuses the skeleton idea only." Never claim code reuse
  while `parking.py` imports nothing from the skeleton.
- [ ] C-9. Pause-and-ask for incomplete applications: today a missing
  driver name or address is a **denial with a reason**, not a pause
  that asks and resumes. If the product wants the hook behaviour in
  `hooks/app2-on-application-incomplete.hook.md`, build it as a
  distinct "Incomplete" state — do not quietly rename Denied.
- [ ] C-10. Screens: application form, rules result, payment,
  permit status / timeline. None exist.
- [ ] C-11. Persistence: applications, active permits, and the ledger
  are in memory only and vanish when the program ends.

## Never tasks (steering, not backlog)

- Never present the demo zones, fees, or plate rules as a real city's
  rules. The DEMO label travels with the numbers everywhere they appear.
- Never wire a real payment method. `kind="demo-payment"` stays until
  a human explicitly decides otherwise.
- Never copy code from any prior parking app into this build.
- Never charge twice for one permit — a second charge is a failed
  test, not a bug to note and ship.
