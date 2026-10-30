# Hook — On wages missing

Applies to: App 1 only.
Format: Markdown hook document. No JSON hook format is claimed.

## Trigger

The rules check needs the person's wages by quarter, and the wage
answers are missing or incomplete — there is no highest quarter to
measure.

## Action — pause and wait

1. PAUSE before the rules check produces any answer.
2. Ask for the missing wage answers, naming the quarters that are
   missing, in plain words.
3. Wait for the answers. Do not run qualification or the WBA table
   on partial wages and present the result as final.

## What must NOT happen

- No guessing wages, no $0 quietly substituted for "unknown," no
  average filled in.
- No "does not qualify" answer built on wages nobody provided.
  Missing wages and low wages are different facts.

## Implementation status (truthful, 2026-10-30)

**Partly reflected in code; the ask-and-wait flow is not built.**

What the code really does today:

- `base_period.highest_quarter([])` returns `0.0`, and a highest
  quarter below $900 makes `monetarily_qualifies()` return `False`
  and `weekly_benefit_amount()` return `0`. That is arithmetic on
  the values given — it does **not** distinguish "wages are missing"
  from "wages are truly low." That distinction is exactly what this
  hook exists to protect, and today nothing in the code makes it.
- Negative wages raise `ValueError` in `wba.py` — the code refuses
  impossible input rather than guessing.

Closing the gap (a real missing-wages state, separate from a
low-wages result) belongs with tasks.md B-9/B-10 when the form and
screens are built.

## Resume condition

Wages for all four base-period quarters are present → run the rules
check (qualification, then WBA).
