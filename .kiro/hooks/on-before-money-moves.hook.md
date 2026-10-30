# Hook — On before money moves

Applies to: BOTH apps. This is the final check before any payment.
Format: Markdown hook document. No JSON hook format is claimed.

## Trigger

Any payment is about to be made — App 1: one certified week.
App 2: one approved permit fee.

## Action — check, then move money once

Before the payment, confirm all four:

1. **Right person** — the payment belongs to this claim / this
   application, no other.
2. **Right item** — App 1: this specific week. App 2: this specific
   application.
3. **Right amount** — App 1: WBA minus the partial-earnings
   deduction, and within the remaining balance (total paid can
   never pass 26 × WBA). App 2: the fee in the `RULES` table for
   that permit type.
4. **Not already paid** — this week / this application has not been
   paid before.

If any check fails: STOP. No money moves. Say why in plain words.

## What must NOT happen

- No double payment, for any reason, including a retry, a double
  click, or a re-run of the demo.
- No payment above the balance cap.
- No payment for App 1's waiting week (it is certified at $0) and
  no payment record at all for App 2's exempt ($0) or denied cases.

## Implementation status (truthful, 2026-10-30)

**Mostly enforced in code — this is the best-built hook.**

App 1 (`claim_flow.py` + skeleton's `MoneyMove` pattern):
- Not already paid: a repeat week raises `DoublePayBlocked` and
  moves no money; `payments` is keyed by week. `skeleton.py`
  `MoneyMove.pay()` does the same with key `record_id:period` and
  `has_paid()` to ask first.
- Right amount / cap: `certify_and_pay()` caps the amount at the
  remaining balance (`max_total − total_paid`); `weekly_payment()`
  applies the partial-earnings deduction first.
- Right order: no paid week before the waiting week is certified
  (`ClaimError`).
- Not enforced as a "person identity" check: the code has no
  identity concept — "right person" today means "this Claim object's
  own week record," nothing stronger. Say so wherever this hook is
  described.

App 2 (`parking.py`):
- Not already paid: `PermitOffice.pay()` returns the existing
  `Payment` on a repeat call and creates nothing new.
- Right amount: the fee is read from the single `RULES` dict.
- No-payment cases: denied or exempt ($0) → `pay()` returns `None`;
  no ledger entry exists.
- Demo truth: the payment is a local ledger entry,
  `kind="demo-payment"`. No real money ever moves in App 2, and in
  App 1 payments are amounts on a demo claim's record, not transfers.

## Resume condition

All four checks pass → exactly one payment is recorded, and the
payment line is added to the person's timeline.
