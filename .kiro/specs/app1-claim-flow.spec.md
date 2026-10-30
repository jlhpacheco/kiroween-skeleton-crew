# Spec — App 1: Claim Flow (California unemployment claims)

## Purpose
Walk one person's claim from filing to a clear timeline, in this order.
Implemented in `app1_unemployment/claim_flow.py` (`Claim`) and shown end-to-end by `app1_unemployment/demo.py`.

## Flow (start to finish)
1. A person files a claim (name + wage record).
2. Identity is checked first, at the door (see hooks: `on-identity-pending`).
3. The rules check runs (see `app1-rules-check.spec.md`): qualify yes/no + weekly benefit amount.
4. One unpaid **waiting week** comes first — it must be certified, and it pays $0.
5. The person certifies every two weeks (see `app1-certification-payment.spec.md`).
6. Payment moves once for each certified week.
7. The person sees a timeline of where the claim stands (`Claim.render_timeline()`).

## Rules of the flow
- No payment before the waiting week is certified.
- No week is paid twice (double-pay is blocked and tested).
- A week with part-time earnings pays the reduced amount from the public disregard rule — never a made-up number.
- The claim stops at 26 paid weeks or the maximum benefit amount, whichever comes first.

## Acceptance
- `app1_unemployment/tests/test_app1.py` claim-flow tests pass.
- Demo (`python3 demo.py` in `app1_unemployment/`): highest quarter $5,200 → WBA $200; waiting week $0; a week with $200 earnings pays $50; total paid $450.
