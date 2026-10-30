# Track C — App 2 (Parking Permits) — Result

- **Hypothesis:** The same 5-step skeleton that runs App 1 (unemployment
  claims) can run a completely different world — parking permits — with
  only a new form, new rules, and new labels. No skeleton change needed.
- **Method:** Built a stdlib-only Python override layer in this folder:
  `parking.py` (form = permit application; rules in ONE `RULES` dict,
  labelled DEMO; steps Applied → Checked → Approved/Denied; money paid
  once, idempotent per application, $0 exempt creates no payment;
  timeline in plain words), `demo.py` running 3 cases, and a unittest
  suite covering each path. Ran the demo and the full suite.
- **Metric:** 13 / 13 unit tests pass. Demo runs clean (exit 0) and
  prints all 3 cases: (1) resident approved + $30 demo payment,
  (2) denied — zone not allowed, no money taken, (3) employee exempt —
  approved at $0 with no payment created. Payment ledger after the
  demo holds exactly 1 payment (case 1 only), proving idempotency
  and the exempt/denied no-money paths.
- **Verdict:** PASS — skeleton reuse proven for App 2. Same 5 steps,
  different world, override layer only.

## Notes

- Rules are DEMO rules (zones North Lot / Downtown / Campus West;
  resident $30, visitor $10, employee exempt $0; plate 4–10 chars;
  one active permit per plate per zone) — not a real city's law.
- This is a NEW Kiroween build from the Oct 30, 2026 window, reusing
  the skeleton idea only. No code was copied from Duvara or Solvia;
  neither was read or modified.
- No network, publishing, GitHub push, or spending was used.
- Board line for the roll-up: Track C App 2 (parking) built in
  `hidden_files/build-2026-10-30/track-c-app2-parking/` — 13/13 tests
  pass; main chat owes Jose Luis the one-line summary.
