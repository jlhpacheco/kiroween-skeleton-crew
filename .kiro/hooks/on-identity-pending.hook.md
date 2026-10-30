# Hook — On identity pending

Applies to: App 1 only. App 2 has no identity check.
Format: Markdown hook document. No JSON hook format is claimed.

## Trigger

The claim reaches the identity check and the person's proof of
identity has not been provided or has not cleared. In the design
pack's flow, identity is checked first, at the door, before the
rules check runs.

## Action — pause and wait

1. PAUSE the claim at the identity step. State stays at that step;
   the claim does not move forward and is not denied for this reason.
2. Tell the person, in plain words, what proof is being waited for.
3. Wait. No rules check, no waiting week, no payment step may start
   while identity is pending.
4. When proof is provided and clears, resume at the rules check.

## What must NOT happen

- No skipping the identity step to "keep things moving."
- No treating a pending identity as a failed identity.
- No inventing an identity rule: what proof EDD accepts is decided by
  EDD's published process, not by this app. If the build ever needs
  the exact rule, it must come from a published EDD source first
  (see steering/public-rules-only.md).

## Implementation status (truthful, 2026-10-30)

**Documented only — there is no identity check in the code.**
`claim_flow.py`, `wba.py`, and `base_period.py` contain no identity
step, field, or function. This hook describes a pause point in the
designed flow (design pack: "Waits for identity proof"). Building it
is tasks.md B-10. No project text may claim identity is checked by
the current build.

## Resume condition

Identity proof provided and cleared → claim proceeds to the rules
check (base period → qualification → WBA).
