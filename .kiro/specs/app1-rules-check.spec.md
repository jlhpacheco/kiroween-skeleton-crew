# Spec — App 1: Rules Check (public EDD rules only)

## Purpose
Decide, from public rules only, whether a claimant qualifies on money and what the weekly benefit amount (WBA) is.
Implemented in `app1_unemployment/wba.py` and `app1_unemployment/base_period.py`.

## The rules (sources: California Unemployment Insurance Code § 1280 and published EDD rules)
1. **Qualify on money:** $1,300 or more in the highest quarter, **or** $900 or more in the highest quarter with total base-period wages of at least 1.25 × the highest quarter.
2. **WBA:** the CUIC § 1280 table. Implemented brackets run $900–$948.99 → $40 up to $1,789–$1,832.99 → $70; above the table, WBA = highest quarter ÷ 26, rounded up to the next dollar. **Floor $40. Cap $450** (the cap is reached at a highest quarter of about $11,674).
3. **Base period — standard:** the first 4 of the last 5 completed calendar quarters before the claim.
4. **Base period — alternate:** the 4 most recently completed quarters (used when the standard period does not qualify the claimant).
5. **Longest run:** 26 weeks. **Top total:** $11,700 at the cap (26 × $450).

## Hard rules for anyone editing this spec or the code
- Public rules only. If a rule is not in a public source, it does not go in.
- Never invent a benefit rule, a table value, or an exception.
- This is a clean-room rebuild from published rules. No EDD COBOL code exists in this project, and none is used, copied, or claimed.

## Acceptance
- WBA tests pin the table edges ($900 → $40, $948.99 → $40, $1,832.99 → $70) and the cap ($450 max, $11,700 max total).
- Base-period tests pin the standard and alternate windows for a known claim date.
