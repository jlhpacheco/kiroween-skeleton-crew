# Steering — Rules in one place, public rules only
All rules for an app live in ONE module for that app (App 1: `wba.py` + `base_period.py` + `claim_flow.py`; App 2: the `RULES` dict in `parking.py`). No rule copies in demos, screens, or docs — docs quote the module, they do not restate a second version.
Same input, same answer, every time.

App 1 uses PUBLIC EDD rules only: CUIC § 1280 weekly benefit table ($40 floor, $450 cap), the qualify test ($1,300 highest quarter, or $900 + total ≥ 1.25× highest quarter), standard and alternate base periods, one unpaid waiting week, certify every two weeks, partial-earnings disregard (greater of $25 or 25%), max 26 weeks / $11,700.
Never invent a benefit rule. If a rule is not in a public source, it does not go in the code.

Clean-room rule: this project is a rebuild from published rules. No EDD COBOL code exists here — none was used, copied, or requested, and California agency software is not public domain (Gov. Code § 7922.585). Never claim a single oldest program, a line count, or a COBOL version — none is published.
App 2's rules are DEMO rules, invented for this build and labeled DEMO in the code. Never present them as a real city's law.
