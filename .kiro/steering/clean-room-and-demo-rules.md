# Steering — Clean room, DEMO labels, stdlib only

Three honesty rules that hold for every file in this project.

## 1. Clean-room rebuild

- This project is a clean-room rebuild from **published rules only**:
  the CUIC §1280 table and formula, the published base-period
  windows, and EDD's published guidance.
- **No EDD COBOL code exists in this project, and none was used.**
  The old SCDB code is not public. Nobody on this project has it,
  read it, or reconstructed it. The module docstring in `wba.py`
  states the standard: "No EDD source code is used, needed, or
  wanted." Keep that standard in every file.
- The same applies sideways: App 2 copies no code from any prior
  parking app. `parking.py` states it does not copy, read, or modify
  Duvara / Solvia. New app = new form + new rules on the skeleton
  pattern, written fresh.
- Never describe this build as a copy, port, or reconstruction of
  SCDB's code. It is a rebuild of the *public rules and the claim
  flow shape*, and that is the whole claim.

## 2. Parking rules are DEMO rules — always labelled

- App 2's zones (North Lot, Downtown, Campus West), fees (resident
  $30 / visitor $10 / employee $0), plate rules (4–10 letters and
  numbers), and the one-permit-per-plate-per-zone rule are **demo
  rules invented for this hackathon**. They are not any city's law,
  fee schedule, or ordinance.
- The DEMO label travels with the numbers: in the `RULES` comment in
  `parking.py`, in the spec, in the README, in demo output, and in
  any submission text. A fee quoted without its DEMO label is a
  defect.
- App 2 payments are demo ledger entries, `kind="demo-payment"`.
  Never describe them as charges, revenue, or real payments.

## 3. Standard library only

- Python standard library only — in the skeleton, in App 1, and in
  App 2. No pip installs, no third-party packages, no network calls
  in code, no database, no external services.
- Money edges are handled with what the stdlib gives: integer cents
  and `Decimal` (`wba.py`, `claim_flow.py`).
- State is in memory only in all three tracks. If a future task adds
  persistence or a UI, it re-checks this rule first and any change
  is an explicit, recorded decision — not a silent import.
- The test suites run with the stdlib alone
  (`python3 -m unittest`), 48/48 passing at build time
  (10 skeleton + 25 App 1 + 13 App 2).
