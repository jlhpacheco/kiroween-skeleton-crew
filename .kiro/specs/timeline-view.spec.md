# Spec — Timeline View (shared by both apps)

## Purpose
Step 5 of the skeleton: the person who filed can always see where their case stands, in plain words.

## Requirements
1. One entry per step that happened: step name, what it means in plain words, and the result (for example, a payment amount).
2. One "next" line: what happens next, and what the person must do (for example, "certify every two weeks").
3. Short sentences. No jargon, no codes, no green-screen abbreviations.
4. The timeline only shows steps that were written down — if a step is not in the log, it does not appear. No invented history.

## Where it lives
- The shared `Timeline` class is in `skeleton/skeleton.py` (ordered entries, `render()` to plain text).
- App 1 renders its claim timeline with the same shape (`Claim.render_timeline()` in `app1_unemployment/claim_flow.py`).
- App 2 prints the same 5-step timeline shape for each permit case (`app2_parking/parking.py`).

## Acceptance
- Both app demos print a numbered, plain-words timeline a first-time reader can follow.
