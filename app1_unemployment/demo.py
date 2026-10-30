"""CLI demo — one example claim, end to end, with a clear timeline.

Run:  python3 demo.py
Stdlib only. Fictional claimant; public rules only.
"""
from __future__ import annotations

import datetime

from base_period import alternate_base_period, highest_quarter, standard_base_period
from claim_flow import Claim
from wba import max_benefit_amount, monetarily_qualifies, weekly_benefit_amount


def main() -> None:
    claim_date = datetime.date(2026, 11, 2)  # a November claim
    wages = [3200.00, 4100.00, 5200.00, 4800.00]  # one amount per base-period quarter

    std = standard_base_period(claim_date)
    alt = alternate_base_period(claim_date)
    hq = highest_quarter(wages)
    total = sum(wages)
    wba = weekly_benefit_amount(hq)
    qualifies = monetarily_qualifies(hq, total)

    print("=== App 1 — California unemployment claim (demo) ===")
    print(f"Claim date: {claim_date}")
    print(f"Standard base period: {std['start']} to {std['end']}  quarters={std['quarters']}")
    print(f"Alternate base period: {alt['start']} to {alt['end']}")
    print(f"Wages by quarter: {wages}")
    print(f"Highest quarter: ${hq:.2f} | Total: ${total:.2f}")
    print(f"Monetarily qualifies: {qualifies}")
    print(f"Weekly benefit amount (CUIC 1280): ${wba}")
    print(f"Maximum in benefit year: ${max_benefit_amount(wba)} (26 weeks x WBA)")
    print()
    if not qualifies:
        print("This claim does not qualify. Timeline stops here.")
        return

    claim = Claim(claimant="Demo Claimant", wba=wba)
    claim.certify_waiting_week()
    claim.certify_and_pay(week=1)                    # no earnings
    claim.certify_and_pay(week=2, earnings=200.00)   # part-time week
    claim.certify_and_pay(week=3)                    # no earnings

    print("--- Timeline (what the person sees) ---")
    print(claim.render_timeline())
    print()
    print(f"Total paid so far: ${claim.total_paid:.2f} | Balance left: ${claim.balance:.2f}")


if __name__ == "__main__":
    main()
