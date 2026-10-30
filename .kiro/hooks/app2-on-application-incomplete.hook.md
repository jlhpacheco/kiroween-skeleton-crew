# Hook — App 2: On application incomplete

Applies to: App 2 only.
Format: Markdown hook document. No JSON hook format is claimed.

## Trigger

A permit application is missing car or address details — in the real
fields of `PermitApplication`: driver name blank, address blank, or
a plate that cannot be read as a plate (after cleaning: not 4–10
characters, or characters other than letters and numbers).

## Intended action — pause and ask

1. PAUSE the application. Do not decide it on missing facts.
2. Say, in plain words, exactly what is missing ("No address on the
   form." — the wording `check_rules()` already produces).
3. Wait for the person to supply it, keeping what was already given.
4. Resume at the rules check with the completed form.

## What must NOT happen

- No guessing a plate, zone, or address.
- No fee taken while an application is incomplete.
- No silent fix-up of a plate beyond the documented cleaning
  (upper-case, spaces and hyphens removed).

## Implementation status (truthful, 2026-10-30)

**Not built as a pause — today's behaviour is a denial.**
`PermitOffice.check_rules()` returns the plain-words reasons above,
and `submit()` then marks the application **Denied**, fee $0, no
money taken, with the reasons on the timeline. The person can read
exactly what was wrong — but the case is closed as Denied, not held
open waiting.

That difference matters and must not be blurred in project text:
this hook describes the *wanted* behaviour; the code does the
*denial* behaviour. Building the pause as its own "Incomplete"
state is tasks.md C-9.

## Resume condition (intended behaviour)

All fields present and the plate cleans to 4–10 letters/numbers →
the rules check runs and the case moves Applied → Checked →
Approved or Denied on the real rules, not on missing facts.
