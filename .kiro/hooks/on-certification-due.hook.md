# Hook — On certification due

Applies to: App 1 only.
Format: Markdown hook document. No JSON hook format is claimed.

## Trigger

It is time for the claimant to certify again — every two weeks —
or the waiting week has not yet been certified. No week may be paid
before it is certified.

## Action — pause and wait

1. PAUSE payment for the uncertified week(s). The claim waits for
   the person, not the other way around.
2. The timeline says, in plain words, what is due: "Next: certify
   every two weeks to keep payments going." (That line is already
   the wording the code appends — see status below.)
3. When the person certifies a week, that week — and only that
   week — may move to payment.
4. The waiting week follows the same rule with one difference: it
   must be certified, and it pays $0.

## What must NOT happen

- No payment for an uncertified week, ever.
- No payment for the waiting week — certifying it does not make it
  payable.
- No second payment when a week is certified twice by mistake
  (see on-before-money-moves.hook.md).

## Implementation status (truthful, 2026-10-30)

**The gate is enforced in code; the reminder/schedule is not.**

- Enforced: `claim_flow.Claim.certify_and_pay()` raises `ClaimError`
  if the waiting week has not been certified first.
  `certify_waiting_week()` records week 0 at $0 and refuses to run
  twice.
- Enforced: one payment per week — a repeat raises
  `DoublePayBlocked`.
- Not built: there is no calendar, reminder, or due-date trigger.
  Nothing notices that two weeks have passed. Weeks are certified
  one at a time when the caller certifies them (the model works one
  week at a time inside each two-week certification — grouping is
  tasks.md B-8).
- Real timeline wording already emitted by `claim_flow.py`:
  "Next: certify every two weeks to keep payments going."

## Resume condition

The week is certified → the before-money-moves check runs → the
week is paid once.
