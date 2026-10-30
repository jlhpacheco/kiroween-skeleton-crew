# Skeleton Crew — One Skeleton, Two Apps

**Form in → rules check → steps move → money moves → person sees a clear timeline.**

That one sentence is the whole template. Swap the form and the rules, keep the skeleton — and the same five steps run two very different apps.

Built for **Kiroween 2026 (Devpost), Skeleton Crew category** — a clean-room rebuild pattern for California's unemployment claims core (SCDB, the Single Client Database: the record book for every CA unemployment claim and payment; claims core built around 1979, called a "45-year-old mainframe-based claims management system" by EDD in 2024, still running in February 2026, replacement planned June 2029). We rebuild from **published rules only** — no EDD COBOL code is used, copied, or claimed (California agency software is not public domain, Gov. Code § 7922.585). We do not claim a single oldest program, a line count, or a COBOL version — none is published.

Pure Python, standard library only. No installs, no network, no database.

## The two apps, side by side

| Step | Skeleton | App 1 — Unemployment claims | App 2 — Parking permits |
|---|---|---|---|
| 1. Form in | A person fills in a form | Claim form: who they are, where they worked, what they earned | Permit application: driver, car plate, address, zone, permit type |
| 2. Rules check | Clear rules say yes or no | Public CA rules: CUIC § 1280 WBA table ($40–$450), base period, waiting week | Car/address allowed? Plate fits, zone allowed, no duplicate |
| 3. Steps move | The case moves step by step | Filed → waiting week → certified every 2 weeks → paid | Applied → Checked → Approved (or Denied, with a plain reason) |
| 4. Money moves | Money moves once, the right amount | One payment per certified week; max 26 weeks / $11,700 | Driver pays the fee once; exempt ($0) issues free, no payment |
| 5. Timeline | The person sees a clear timeline | Claim status and next steps in plain words | Permit status in plain words |

App 1's rules are real public rules (see `.kiro/specs/app1-rules-check.spec.md`). App 2's rules are **demo rules**, invented for this build and labeled DEMO in the code — not a real city's law. Both apps **run on the one skeleton engine** (`skeleton/skeleton.py`, class `Case`): each app is an override layer only — new form fields, new rules callable, new step labels, new timeline words. The intake, the rules contract, the step machine, the pay-once ledger, and the timeline machinery are the skeleton's, shared — and each app carries proof tests (`tests/test_shared_skeleton.py`) that fail if that ever stops being true.

## Setup and run

**Setup (once, for both apps)** — there is nothing to install; this only checks you have Python 3:

```bash
python3 --version
```

**Run App 1 — unemployment claims demo:**

```bash
python3 app1_unemployment/demo.py
```

**Run App 2 — parking permits demo:**

```bash
python3 app2_parking/demo.py
```

## Tests (58 total)

```bash
cd skeleton && python3 -m unittest test_skeleton -v && cd ..
cd app1_unemployment && python3 -m unittest discover -s tests -v && cd ..
cd app2_parking && python3 -m unittest discover -s tests -v && cd ..
```

Skeleton 10 · App 1 rules/flow 25 + shared-engine proof 6 · App 2 permits 13 + shared-engine proof 4.

## Layout

| Path | What it is |
|---|---|
| `skeleton/` | The template: `skeleton.py` — the `Case` engine over Intake, RulesCheck, StepMachine, MoneyMove, Timeline + its tests and README |
| `app1_unemployment/` | App 1: `wba.py` (§ 1280 table), `base_period.py`, `claim_flow.py` (a `Claim` = one skeleton `Case` + claim rules), `demo.py`, `tests/` |
| `app2_parking/` | App 2: `parking.py` (rules in one `RULES` dict, cases run on the shared engine), `demo.py`, `tests/`, README |
| `.kiro/` | Kiro files at the repo root: `specs/`, `hooks/`, `steering/` — the real build instructions for this project |
| `docs/` | Submission drafts (Devpost page draft, setup notes, credits-request sheet) and per-track build results |

## How Kiro was used

Honest status key: **USED** = done in this project · **DOC** = real files written, describing the design (not executed by the Kiro runtime in this local build) · **TO-DO** = not done yet · **NOT USED** = not needed.

| Kiro feature | What it did in this project | Status |
|---|---|---|
| **Spec-driven development** | Specs were written before code (design pack, Oct 27) and now live as real files in `.kiro/specs/`: a skeleton-core spec and a timeline spec, plus full folder specs (requirements / design / tasks) for App 1 and App 2. The code follows them module-for-module, and the task lists mark honestly what is built and what is not yet. | USED |
| **Steering docs** | Plain-language build rules in `.kiro/steering/` (6 files): build the 5 bones in order; rules in one place; public EDD rules only, never invent a benefit rule; clean-room (no EDD COBOL); plain words; pay once, never twice. | USED |
| **Agent Hooks** | The flow's pause-and-wait points are written as hook files in `.kiro/hooks/`: form incomplete, identity pending, wages missing, certification due, staff review needed, final check before money moves, App 2 application incomplete. | DOC |
| **Vibe coding** | No Kiro IDE vibe-coding session has been run yet. The first build (Oct 30, 2026) was written by an agent swarm working from the design pack and these specs. | TO-DO |
| **MCP** | No MCP server was needed for this build (stdlib-only, public rules already in hand). | NOT USED — not needed |

## Status

Local build, assembled Oct 30, 2026 — new project, built inside the Kiroween submission window. Not yet hosted, not yet submitted. Sample people and cars are fictional. Deadline: Friday, December 4, 2026, 2:00 PM PT.
