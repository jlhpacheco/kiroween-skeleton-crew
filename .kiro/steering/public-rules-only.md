# Steering — Public EDD rules only. Never invent a benefit rule.

App 1 follows **only** the published public rules of California
unemployment insurance, as listed below. This list is the whole
authority. If a rule is not on this list and cannot be traced to a
published source, it does not go in the code, the specs, or the
submission text.

## The rule list (as implemented, 2026-10-30)

| Rule | Value | Implemented in |
|---|---|---|
| Weekly Benefit Amount table, CUIC §1280 | Highest-quarter wages $900.00–$1,832.99 → WBA $40 rising to $70, by the published step table | `wba.py` `_TABLE` |
| WBA above the table | Highest quarter ÷ 26, rounded up to the next whole dollar | `wba.weekly_benefit_amount()` |
| WBA floor / cap | $40 minimum, $450 maximum | `wba.py` `MIN_WBA` / `MAX_WBA` |
| Money qualification, Branch A | Highest quarter ≥ $1,300 | `wba.monetarily_qualifies()` |
| Money qualification, Branch B | Highest quarter ≥ $900 **and** total base-period wages ≥ 1.25 × highest quarter | `wba.monetarily_qualifies()` |
| Standard base period | The first 4 of the last 5 completed calendar quarters before the claim begins (window by claim month, UIC §1275 / EDD DE 1545I as cited in code) | `base_period.standard_base_period()` |
| Alternate base period | The 4 most recently completed quarters; used when the standard period does not qualify | `base_period.alternate_base_period()` (fallback selection into the flow is not yet wired — tasks.md B-6) |
| Waiting week | First week of the claim: must be certified, paid $0 | `claim_flow.Claim.certify_waiting_week()` |
| Certification | The claimant certifies every 2 weeks (the model certifies/pays one week at a time inside each certification) | `claim_flow.Claim.certify_and_pay()` |
| Partial-earnings disregard | The **greater of $25 or 25%** of the week's earnings is disregarded; the rest is deducted dollar-for-dollar from the WBA; a week never pays below $0 | `claim_flow.partial_earnings_deduction()` |
| Longest run | 26 payable weeks maximum | `claim_flow.py` `MAX_WEEKS` |
| Top total | 26 × WBA; at the $450 cap, **$11,700** | `wba.max_benefit_amount()` |

## Rules for the builder

- **Never invent a benefit rule.** No made-up waiting period, fee,
  penalty, deadline, earnings rule, or eligibility test — in code,
  in a spec, in demo data presented as a rule, or in submission copy.
- A rule with no source is a **stop**: flag the gap, name the
  published source that would settle it, and wait. (House rule behind
  this: no fake data — a fact with no field or no source is reported
  as missing, never manufactured.)
- When a public source and an older project note disagree, the
  published source wins and the note gets corrected. Example already
  in this build's history: the design pack called §1280 a "rule of
  thumb: highest quarter divided by 26" — the code implements the
  actual published step table for $900–$1,832.99 and uses ÷26 only
  above the table, because that is what the statute table says.
- Non-money eligibility (job separation, able and available, work
  search, appeals, fraud, overpayments) is **not implemented** and
  must never be implied. The build decides money qualification,
  waiting week, certification payment, and nothing else.
- About SCDB itself, claim only what public sources state: it is the
  Single Client Database, EDD's mainframe record system for claims
  and payments, with a claims core dating to about 1979 (EDD's own
  "45-year-old mainframe-based claims management system" wording,
  2024). No single oldest program and no line count is published —
  do not invent either.
