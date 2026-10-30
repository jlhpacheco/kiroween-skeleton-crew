# Hook — On staff review needed

Applies to: App 1 (claim questions a person must decide) and App 2
(any case a human must look at, if a staff flow is ever built).
Format: Markdown hook document. No JSON hook format is claimed.

## Trigger

The rules reach a point they do not decide — a question the
published rules leave to a human, or a fact that does not fit the
form. Examples of the *kind* of trigger (not new rules): conflicting
wage answers, a fact pattern the form has no field for.

## Action — pause and wait

1. PAUSE the case at its current step. The step history already
   written down stays written down.
2. Route the case to a human, with the timeline and the exact
   question that needs a person.
3. Wait for the staff answer. Record the answer as a new timeline
   line, in plain words, when it arrives.
4. Resume from the paused step — never restart the case.

## What must NOT happen

- The app never decides a human question by guessing, and never
  invents a rule to avoid pausing (see
  steering/public-rules-only.md: a rule with no published source is
  a stop, not a gap to fill).
- A case in staff review is never shown to the person as denied.
  Waiting is its own state and the timeline says so.

## Implementation status (truthful, 2026-10-30)

**Documented only.** Neither app has a staff view, a review queue,
or a review state:

- App 1's `Claim` has no staff-review state; its states are
  `Filed → WaitingWeek → Certified → Paid`. Non-monetary questions
  (why a job ended, able-and-available, appeals) are outside the
  code entirely — the build decides money qualification only.
- App 2's `PermitOffice` has no review path; a case is Approved or
  Denied by `check_rules()` alone.

Building the pause is tasks.md B-10 (App 1). Until then, this hook
is a design requirement, not a feature.

## Resume condition

A staff answer is recorded → the case resumes at the step where it
paused, with the answer on the timeline.
