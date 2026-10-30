# Tasks — App 1: Unemployment Claims

Corresponds to: `specs/app1-unemployment-claims/requirements.md` and
`design.md`. Checkboxes tell the truth about 2026-10-30: `[x]` = built
and test-proven in Track B; `[ ]` = not built.

## Built and proven (Track B, 25/25 tests)

- [x] B-1. `wba.py` — §1280 step table $900.00–$1,832.99 → $40–$70;
  above the table `ceil(highest quarter / 26)`; floor $40, cap $450;
  below $900 → 0. (Req. 2)
- [x] B-2. `wba.monetarily_qualifies()` — Branch A: highest quarter
  ≥ $1,300. Branch B: ≥ $900 and total ≥ 1.25 × highest quarter.
  (Req. 1)
- [x] B-3. `base_period.py` — standard (first 4 of last 5 completed
  quarters) and alternate (4 most recent) windows by claim month;
  `highest_quarter()`. (Req. 3, criteria 1–4)
- [x] B-4. `claim_flow.py` — waiting week first, certified, $0, before
  any paid week; double-certification blocked. (Req. 4)
- [x] B-5. `claim_flow.py` — certify-and-pay weeks 1–26, one payment
  per week (`DoublePayBlocked` on a repeat), partial-earnings
  disregard = greater of $25 or 25%, balance cap 26 × WBA
  ($11,700 at the $450 cap). (Req. 5, 6)
- [x] B-5b. Plain-language timeline appended at every step and
  rendered as a numbered list. (Req. 7)
- [x] B-5c. `demo.py` — Nov 2026 worked example: highest quarter
  $5,200 → WBA $200; waiting $0; $200-earnings week pays $50;
  total shown $450.

## Not built — next tasks, in order

- [ ] B-6. Wire alternate-base-period fallback into the flow: try
  standard first; if it does not monetarily qualify, re-check with
  the alternate period's wages before saying no. Today `demo.py`
  only prints both periods; `claim_flow.py` never selects between
  them. (Req. 3 — the honest gap)
- [x] B-7. DONE (refactor, Oct 30, 2026): App 1 runs literally on
  Track A's `skeleton.py`. `Claim` builds one skeleton `Case`
  (engine Intake / `claim_rules` / StepMachine / MoneyMove /
  Timeline) and pays every week through `Case.pay`;
  `claim_flow.DoublePayBlocked` is the skeleton's class. Proof:
  `tests/test_shared_skeleton.py` (6 tests — engine parts, pay-spy,
  class identity). All 25 Track B tests pass unchanged; demo total
  still $450.00. Project text now says "built on the skeleton code."
- [ ] B-8. Biweekly certification grouping: today the model certifies
  and pays one week at a time. Group weeks into the real two-week
  certification the design pack describes, keeping one payment per
  week inside it.
- [ ] B-9. Screens (design pack outline, none exist): claim form,
  identity check, wages (4 quarters), rules result, waiting week,
  certification, payment history, timeline, staff view, help/error.
  Plain words on every screen (see steering/plain-words.md).
- [ ] B-10. Identity-check pause and staff-review pause as working
  flow states (today they exist only as hook documents in `hooks/`).
- [ ] B-11. Persistence: a saved claim record that survives a restart.
  Today all state is in memory and is lost when the program ends.

## Never tasks (steering, not backlog)

- Never add a benefit rule that is not in the published sources in
  `steering/public-rules-only.md`.
- Never import, reconstruct, or claim access to EDD COBOL / SCDB code.
- Never connect to a real EDD system or use a real person's data.
- Never let a week be paid twice — a duplicate payment is a failed
  test, not a bug to note and ship.
