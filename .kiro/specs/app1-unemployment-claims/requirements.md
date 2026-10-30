# Spec — App 1: Unemployment Claims (California)

Feature name: `app1-unemployment-claims`
Status: Requirements describe the code that exists (Track B, 2026-10-30),
plus clearly marked future work. Code: `wba.py`, `base_period.py`,
`claim_flow.py`, `demo.py`. Tests: 25/25 pass at draft time.

## Introduction

App 1 is a clean-room rebuild of the core of a California unemployment
insurance claim — the part the old EDD Single Client Database (SCDB)
handles — using **only published public rules**. One sentence:

Form in → rules check → steps move → money moves → person sees a timeline.

It is a demonstration and a rebuild study. It is not EDD's system, it
does not connect to EDD, and it makes no real benefit payments.

## Glossary

- **Claimant** — the person filing.
- **WBA** — Weekly Benefit Amount.
- **Base period** — the four quarters of wages the claim is measured on.
- **Highest quarter** — the base-period quarter with the most wages.
- **Waiting week** — the first week of a claim. It must be certified.
  It is not paid.
- **Certification** — the claimant's regular report that a week is
  claimed. In real life it is done every two weeks.
- **Skeleton** — the shared 5-step template in `skeleton.py` (Track A).

## Requirements

### Requirement 1 — Monetary qualification (public rule only)

**User story:** As a claimant, I want a yes/no answer on whether my
wages qualify, from the published rule, so the same wages always give
the same answer.

Acceptance criteria:

1. WHEN the highest quarter is $1,300 or more, THE SYSTEM SHALL say
   the claim monetarily qualifies (Branch A).
2. WHEN the highest quarter is $900 or more AND total base-period
   wages are at least 1.25 × the highest quarter, THE SYSTEM SHALL say
   the claim monetarily qualifies (Branch B).
3. WHEN the highest quarter is below $900, THE SYSTEM SHALL say the
   claim does not monetarily qualify — neither branch can pass.
4. WHEN wages are negative, THE SYSTEM SHALL raise an error, not guess.
5. This test SHALL live in one place only: `wba.monetarily_qualifies()`.

### Requirement 2 — Weekly Benefit Amount, CUIC §1280

**User story:** As a claimant, I want my weekly amount set by the
published §1280 table, not by anyone's judgment.

Acceptance criteria:

1. WHEN highest-quarter wages are $900.00–$1,832.99, THE SYSTEM SHALL
   use the published §1280 step table ($40 rising to $70).
   Implemented as the `_TABLE` brackets in `wba.py`.
2. WHEN highest-quarter wages are above $1,832.99, THE SYSTEM SHALL
   compute WBA as highest quarter ÷ 26, rounded **up** to the next
   whole dollar.
3. THE SYSTEM SHALL apply a floor of $40 and a cap of $450 to every WBA.
4. WHEN the highest quarter is below $900, THE SYSTEM SHALL return a
   WBA of 0 (no benefit amount exists).
5. Worked check: highest quarter $5,200 → WBA $200.

### Requirement 3 — Base period (standard and alternate)

**User story:** As a claimant, I want the right four quarters used,
and the alternate period tried when the standard one does not qualify.

Acceptance criteria:

1. THE SYSTEM SHALL compute the **standard base period** as the first
   four of the last five completed calendar quarters before the claim
   begins (`base_period.standard_base_period()`).
2. THE SYSTEM SHALL compute the **alternate base period** as the four
   most recently completed quarters
   (`base_period.alternate_base_period()`).
3. Both SHALL be selected by claim month, using the quarter-window
   table in `base_period.py` (sourced in its docstring to UIC §1275
   and EDD DE 1545I).
4. THE SYSTEM SHALL report the highest quarter across the four
   quarters used (`base_period.highest_quarter()`).

   Note on the real code: `demo.py` computes both periods and prints
   both. Automatic "try standard, fall back to alternate if it does
   not qualify" selection is **not** wired into `claim_flow.py` —
   see tasks.md, Task B-6.

### Requirement 4 — Waiting week first, unpaid

Acceptance criteria:

1. THE SYSTEM SHALL require the waiting week to be certified before
   any paid week. Paying a week first SHALL raise `ClaimError`.
2. THE SYSTEM SHALL pay $0 for the waiting week and record it as
   week 0 (`claim_flow.Claim.certify_waiting_week()`).
3. Certifying the waiting week twice SHALL raise `ClaimError`.

### Requirement 5 — Certify, then pay once per week

Acceptance criteria:

1. THE SYSTEM SHALL certify and pay one week at a time, weeks 1–26.
   (In real life the claimant certifies every two weeks; the model
   handles one week at a time inside each certification.)
2. A second payment attempt for the same week SHALL raise
   `DoublePayBlocked` and move no money.
3. THE SYSTEM SHALL pay at most 26 payable weeks.
4. Total paid SHALL never exceed 26 × WBA. At the $450 cap that total
   is $11,700 (`wba.max_benefit_amount()`).

### Requirement 6 — Partial earnings

Acceptance criteria:

1. WHEN a claimant reports earnings for a week, THE SYSTEM SHALL
   disregard the **greater of $25 or 25% of that week's earnings**.
2. THE SYSTEM SHALL deduct the rest dollar-for-dollar from the WBA.
3. A week's payment SHALL never be below $0 and the deduction never
   above the WBA (`claim_flow.partial_earnings_deduction()`).
4. Worked check: WBA $200, earnings $200 → disregard $50,
   deduction $150, payment $50.

### Requirement 7 — Plain-language timeline

Acceptance criteria:

1. Every step — filed, waiting week, each certified/paid week, claim
   complete — SHALL add one plain-words line to the timeline, in order.
2. Each payment line SHALL state the week and the amount; a week with
   earnings SHALL state the earnings reported.
3. THE SYSTEM SHALL render the timeline as a numbered list a claimant
   can read (`Claim.render_timeline()`).
4. No line SHALL use jargon a claimant would need explained.

### Requirement 8 — Rules in one place, stdlib only, clean room

1. WBA and qualification rules SHALL live only in `wba.py`. Base-period
   rules SHALL live only in `base_period.py`. Payment-flow rules SHALL
   live only in `claim_flow.py`. No rule copies elsewhere.
2. THE SYSTEM SHALL use the Python standard library only. No installs,
   no network calls in code.
3. THE SYSTEM SHALL NOT contain, copy, or claim to use any EDD COBOL
   code. No such code is public, none exists in this project, and none
   was used. Rules come from the published statute and EDD's published
   guidance only.
4. WHEN a benefit rule is not in the published sources listed in
   steering, THE SYSTEM SHALL NOT invent it. Missing rule = stop and
   flag, never fill in.

## Out of scope for this spec (future work, not built)

- Any screen or web UI (claim form, identity check, wages, rules
  result, waiting-week, certification, payment history, timeline,
  staff view, help/error — all from the design pack outline).
- Identity verification of any kind.
- Persistence / database; claim state is in memory only.
- Real payments, real claimant data, any EDD connection.
- Non-monetary eligibility (separation reasons, able-and-available,
  appeals, overpayments). The code does not decide these and this spec
  does not claim it does. See Gap 3 in the draft README/tasks.
