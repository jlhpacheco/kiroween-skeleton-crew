"""Base period — California UI (UIC section 1275; EDD DE 1545I).

Standard base period = the first four of the last five completed
calendar quarters before the claim begins. By claim month (confirmed
in the Oct 29, 2026 prep doc):
- Jan-Mar claim -> period ends Sep 30 of the prior year
- Apr-Jun claim -> period ends Dec 31 of the prior year
- Jul-Sep claim -> period ends Mar 31 of the claim year
- Oct-Dec claim -> period ends Jun 30 of the claim year

Alternate base period (used when the standard period does not
monetarily qualify) = the four most recently completed quarters:
- Jan-Mar claim -> ends Dec 31 prior year
- Apr-Jun claim -> ends Mar 31 of the claim year
- Jul-Sep claim -> ends Jun 30 of the claim year
- Oct-Dec claim -> ends Sep 30 of the claim year

A "quarter" here is (year, quarter_number 1-4). Stdlib only.
"""
from __future__ import annotations

import datetime
from typing import List, Tuple

Quarter = Tuple[int, int]  # (year, 1..4)

_QUARTER_END = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}
_QUARTER_START = {1: (1, 1), 2: (4, 1), 3: (7, 1), 4: (10, 1)}


def _shift(q: Quarter, n: int) -> Quarter:
    """Move a quarter n quarters forward (negative = backward)."""
    y, qq = q
    idx = y * 4 + (qq - 1) + n
    return (idx // 4, idx % 4 + 1)


def _four_ending_at(end: Quarter) -> List[Quarter]:
    return [_shift(end, -3), _shift(end, -2), _shift(end, -1), end]


def _period(quarters: List[Quarter]) -> dict:
    first, last = quarters[0], quarters[-1]
    sm, sd = _QUARTER_START[first[1]]
    em, ed = _QUARTER_END[last[1]]
    return {
        "quarters": list(quarters),
        "start": datetime.date(first[0], sm, sd),
        "end": datetime.date(last[0], em, ed),
    }


def _claim_year_month(claim) -> Tuple[int, int]:
    if isinstance(claim, datetime.date):
        return claim.year, claim.month
    year, month = claim  # (year, month) tuple
    return int(year), int(month)


def standard_base_period(claim) -> dict:
    """First four of the last five completed quarters, by claim month."""
    year, month = _claim_year_month(claim)
    if 1 <= month <= 3:
        end = (year - 1, 3)
    elif 4 <= month <= 6:
        end = (year - 1, 4)
    elif 7 <= month <= 9:
        end = (year, 1)
    elif 10 <= month <= 12:
        end = (year, 2)
    else:
        raise ValueError("month must be 1-12")
    return _period(_four_ending_at(end))


def alternate_base_period(claim) -> dict:
    """Four most recently completed quarters, by claim month."""
    year, month = _claim_year_month(claim)
    if 1 <= month <= 3:
        end = (year - 1, 4)
    elif 4 <= month <= 6:
        end = (year, 1)
    elif 7 <= month <= 9:
        end = (year, 2)
    elif 10 <= month <= 12:
        end = (year, 3)
    else:
        raise ValueError("month must be 1-12")
    return _period(_four_ending_at(end))


def highest_quarter(wages_by_quarter) -> float:
    """Highest value among per-quarter wage amounts (0.0 if empty)."""
    vals = list(wages_by_quarter)
    return max(vals) if vals else 0.0
