"""Weekly Benefit Amount (WBA) — California UI Code section 1280.

Clean-room implementation from the PUBLIC statute table and formula.
No EDD source code is used, needed, or wanted.

Rules (CUIC section 1280, as confirmed in the Oct 29, 2026 prep doc):
- Highest-quarter wages $900.00-$1,832.99: step table, $40 rising to $70.
  Brackets below are the published section 1280 table brackets.
- Above $1,832.99: WBA = highest-quarter wages / 26, rounded UP to the
  next whole dollar (the statute's "50% of wages divided by 13").
- Floor $40, cap $450 (claims effective on/after Jan 1, 2005).

Monetary qualification (section 1276 / 1280):
- Branch A: highest quarter >= $1,300, OR
- Branch B: highest quarter >= $900 AND total base-period wages
  >= 1.25 x highest-quarter wages.
Below $900 in the highest quarter, neither branch can pass.

Money is handled in integer cents / Decimal so edges are exact.
Stdlib only.
"""
from __future__ import annotations

import math
from decimal import Decimal

MIN_WBA = 40
MAX_WBA = 450

# Published step table: (low_cents_inclusive, high_cents_inclusive, wba_dollars)
_TABLE = [
    (90000, 94899, 40), (94900, 97499, 41), (97500, 100099, 42),
    (100100, 102699, 43), (102700, 105299, 44), (105300, 107899, 45),
    (107900, 111799, 46), (111800, 114399, 47), (114400, 116999, 48),
    (117000, 119599, 49), (119600, 122199, 50), (122200, 124799, 51),
    (124800, 128699, 52), (128700, 131299, 53), (131300, 133899, 54),
    (133900, 136499, 55), (136500, 140399, 56), (140400, 142999, 57),
    (143000, 145599, 58), (145600, 149499, 59), (149500, 152099, 60),
    (152100, 154699, 61), (154700, 158599, 62), (158600, 161199, 63),
    (161200, 163799, 64), (163800, 167699, 65), (167700, 170299, 66),
    (170300, 174199, 67), (174200, 176799, 68), (176800, 180699, 69),
    (180700, 183299, 70),
]

TABLE_TOP_CENTS = 183299  # $1,832.99 -> $70, last table bracket


def _to_cents(wages) -> int:
    """Exact dollars-and-cents -> cents (str/Decimal-safe)."""
    return int(Decimal(str(wages)) * 100)


def weekly_benefit_amount(highest_quarter_wages) -> int:
    """Return the WBA in whole dollars for a highest-quarter wage amount.

    Raises ValueError for negative wages. Returns 0 when the highest
    quarter is below the $900 table floor (no benefit amount exists;
    monetary qualification also fails there — see monetarily_qualifies).
    """
    cents = _to_cents(highest_quarter_wages)
    if cents < 0:
        raise ValueError("wages must not be negative")
    if cents < 90000:
        return 0
    if cents <= TABLE_TOP_CENTS:
        for low, high, wba in _TABLE:
            if low <= cents <= high:
                return wba
        raise AssertionError("table gap")  # brackets are contiguous
    # Above the table: ceil(highest_quarter / 26), floored/capped.
    wba = math.ceil(Decimal(cents) / Decimal(100) / Decimal(26))
    return max(MIN_WBA, min(MAX_WBA, int(wba)))


def monetarily_qualifies(highest_quarter_wages, total_base_period_wages) -> bool:
    """True if either monetary-qualification branch passes."""
    hq = Decimal(str(highest_quarter_wages))
    total = Decimal(str(total_base_period_wages))
    if hq < 0 or total < 0:
        raise ValueError("wages must not be negative")
    if hq >= Decimal("1300"):
        return True  # Branch A
    if hq >= Decimal("900") and total >= Decimal("1.25") * hq:
        return True  # Branch B
    return False


def max_benefit_amount(wba: int) -> int:
    """Maximum payable in a benefit year at this WBA: 26 weeks of WBA.
    At the $450 cap that is $11,700."""
    return 26 * int(wba)
