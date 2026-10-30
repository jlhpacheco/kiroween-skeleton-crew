# Steering — Rules in one place only

Every rule lives in exactly one place. Same input, same answer,
every time.

## Where the rules live in this project (the real homes)

| Rules | One home |
|---|---|
| The skeleton's contract: a rules check is one callable returning qualify + amount + plain reason | `skeleton.py` — `RulesCheck` / `run_rules()` |
| WBA table + money qualification (CUIC §1280) | `wba.py` — `_TABLE`, `weekly_benefit_amount()`, `monetarily_qualifies()` |
| Base-period windows | `base_period.py` — `standard_base_period()`, `alternate_base_period()` |
| Waiting week, certification, partial earnings, caps | `claim_flow.py` — `Claim`, `partial_earnings_deduction()` |
| ALL parking rules (DEMO) | `parking.py` — the `RULES` dict + `PermitOffice.check_rules()` |

## Rules for the builder

- Need a rule changed? Change it in its one home, then re-run that
  track's tests. Never patch a copy of a rule in a screen, a demo,
  a test helper, or a document.
- A demo may *call* the rules. It may never restate a number the
  rules own. (`demo.py` in both apps calls the functions; the WBA
  and fee numbers in the demos come out of the rule modules.)
- Documents quote the rules; they do not become a second source.
  If a document and the code disagree, the code's one home wins and
  the document gets fixed.
- Machinery lives in one home too: since the Oct 30, 2026 refactor
  (tasks.md B-7 / C-8, both DONE), App 1 and App 2 import
  `skeleton.py` and run on its `Case` engine — neither app
  re-implements pay-once, steps, intake, or timeline machinery.
  Never re-introduce a private copy of that machinery inside an app;
  each app's `tests/test_shared_skeleton.py` exists to catch it.
- Deterministic only: no randomness, no clock-dependent amounts, no
  network lookups in a rules check. The same record checked twice
  gives the same result twice.
