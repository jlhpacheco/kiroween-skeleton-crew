# Spec — App 2: Parking Permits (DEMO rules)

Feature name: `app2-parking-permits`
Status: Requirements describe the code that exists (Track C, 2026-10-30).
Code: `parking.py`, `demo.py`. Tests: 13/13 pass at draft time.

> **DEMO RULES — read first.** Every parking rule in this app is a
> demo rule invented for this hackathon build. The zones, fees, and
> plate rules are **not** a real city's law, fee schedule, or
> ordinance, and must never be presented as one. The code says so in
> its own header and in the `RULES` comment, and so does this spec.

## Introduction

App 2 exists to prove one point: the same 5-step skeleton that runs an
unemployment claim also runs a completely different job, with only the
form and the rules swapped.

Form in → rules check → steps move → money moves → person sees a timeline.

It is a new build for Kiroween 2026. It does not copy any prior
parking app — `parking.py` states: no code is copied from Duvara /
Solvia; they are "not copied, read, or modified here."

## Glossary

- **Application** — one permit request (`PermitApplication`).
- **Zone** — one of the demo parking zones.
- **Plate** — the car plate, cleaned: upper-cased, spaces and hyphens
  removed (`clean_plate()`).
- **Exempt** — a permit type that never pays (in this demo: employee).

## Requirements

### Requirement 1 — The form

**User story:** As a driver, I want to apply with plain facts: who I
am, my car, my address, my zone, and my permit type.

Acceptance criteria:

1. THE SYSTEM SHALL take five fields: `driver`, `plate`, `address`,
   `zone`, `permit_type` (`resident` | `visitor` | `employee`).
2. Each submitted application SHALL get its own ID, in order:
   `APP-001`, `APP-002`, …

### Requirement 2 — Rules check, in one place, with plain reasons

Acceptance criteria:

1. ALL parking rules SHALL live in one dict, `RULES`, in `parking.py`,
   and in the one check that reads it, `PermitOffice.check_rules()`.
   No rule copies elsewhere.
2. THE SYSTEM SHALL fail an application, with a plain-words reason
   for each failure, WHEN any of these is true:
   - driver name is blank → "No driver name on the form."
   - address is blank → "No address on the form."
   - zone is not one of the demo allowed zones: **North Lot,
     Downtown, Campus West**.
   - permit type is not known (not `resident`, `visitor`, `employee`).
   - cleaned plate is not 4–10 characters long.
   - cleaned plate has characters other than letters and numbers.
   - the same plate already has an active permit for the same zone
     (one active permit per plate per zone).
3. An empty reason list SHALL mean the application passes.

### Requirement 3 — Steps move, in order

Acceptance criteria:

1. Every application SHALL move `Applied → Checked → Approved`, or
   `Applied → Checked → Denied`. No other path exists.
2. THE SYSTEM SHALL record the steps the case actually went through
   on the result (`PermitResult.steps`).

### Requirement 4 — Money moves once, or not at all

Acceptance criteria:

1. Demo fees SHALL be: resident **$30**, visitor **$10**,
   employee **$0 (exempt)**.
2. WHEN an application is approved and not exempt, THE SYSTEM SHALL
   record exactly one payment, `PAY-<application_id>`, with
   `kind="demo-payment"`. It is a local ledger entry that stands in
   for a payment. It is never a real charge.
3. Calling `pay()` again for the same application SHALL return the
   same payment and charge nothing extra (idempotent).
4. WHEN an application is exempt ($0), THE SYSTEM SHALL create no
   payment at all. `pay()` returns `None`.
5. WHEN an application is denied, THE SYSTEM SHALL take no money and
   set the fee to $0.

### Requirement 5 — Plain-language timeline

Acceptance criteria:

1. The applicant SHALL be able to see the case in plain words
   (`PermitOffice.status_timeline(application_id)`): applied line
   (driver, type, plate, zone), checked line (rules say yes / no),
   decision line, money line, and a final status line.
2. A denied case SHALL list every denial reason in plain words and
   end with "Status: Denied. No money was taken."
3. An approved paid case SHALL end with "Status: Approved, paid, and
   active. You can park." An exempt case SHALL say the permit is free
   and no payment was needed.
4. Asking for an unknown application ID SHALL return a plain
   "No application <id>." line, not an error screen.

### Requirement 6 — Skeleton reuse, honestly stated

1. App 2 SHALL follow the skeleton's 5 steps and step names' meaning.
2. Project text SHALL say App 2 reuses the skeleton **idea / pattern**.
   It does NOT import `skeleton.py` — `parking.py` is a standalone
   override layer (`PermitOffice` holds its own steps, ledger, and
   timeline lists). Claiming code reuse would be false. See tasks.md.

### Requirement 7 — Build constraints

1. Standard library only. No network, no files, no real payments.
2. All state is in memory only (`PermitOffice` dicts) and is lost
   when the program ends. This SHALL be stated wherever persistence
   might be assumed.

## Out of scope for this spec (not built)

- Any screen or web UI, permit printing, or a public verify page.
- Real zones, real fees, real city rules of any kind.
- Renewals, expiry dates, appeals of a denial, refunds.
- More than one car per application; transfers between zones.
