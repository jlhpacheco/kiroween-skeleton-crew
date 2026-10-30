# Spec — App 1: Certification and Payment

## Purpose
Pay the right amount, once, for each certified week. Implemented in `app1_unemployment/claim_flow.py`.

## Requirements
1. **Waiting week first.** Week 0 must be certified; it pays $0. No exceptions.
2. **Certify every two weeks.** Each certified week is paid once, in order.
3. **Part-time work (partial-earnings disregard).** EDD ignores the greater of $25 or 25% of the week's earnings; the rest is taken off that week's benefit. A week never pays less than $0.
   - Worked check: WBA $200, earnings $200 → disregard $50 → payment $50.
4. **Pay once, never twice.** Paying the same week again is blocked (`DoublePayBlocked`) and covered by a test.
5. **Stop at the limit.** Payments stop at 26 weeks or when the maximum benefit amount for the benefit year is reached.

## Acceptance
- Tests cover: waiting week $0, plain week full WBA, part-time week reduced, double-pay blocked, 26-week / maximum-amount stop.
