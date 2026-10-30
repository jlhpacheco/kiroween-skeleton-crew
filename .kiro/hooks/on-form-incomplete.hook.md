# Hook — On form incomplete

Applies to: App 1 (claim form) and App 2 (permit application form).
Format: Markdown hook document. No JSON hook format is claimed —
none was confirmed against Kiro's docs at draft time.

## Trigger

A form is started but not finished — required answers are missing
when the person tries to move on.

## Action — pause and wait

1. PAUSE. Do not submit a partial form. Do not create a claim or an
   application from half a form.
2. Say, in plain words, exactly which answers are missing.
3. Wait for the person to finish the form.
4. Resume at the same form, with the answers already given kept —
   never make the person start over.

## What must NOT happen

- No guessing a missing answer.
- No default answer filled in silently.
- No partial record passed to the rules check.

## Implementation status (truthful, 2026-10-30)

**Documented only.** There is no form and no UI in the build yet —
both apps are Python library + CLI demo. The closest real behaviour:

- App 2: a missing driver name or address is caught by
  `PermitOffice.check_rules()` and becomes a **denial with a plain
  reason**, not a pause-and-resume. Closing that gap is tasks.md C-9.
- App 1: `skeleton.py` `Intake.submit()` rejects an empty form
  (`ValueError: form must not be empty`) and a non-dict form. It does
  not check for individual missing answers.

## Resume condition

All required answers present → the form may be submitted and the
rules check may run.
