# Devpost Page — DRAFT ONLY

> **Status: DRAFT — NOT SUBMITTED, NOT PUBLISHED**
> Project: Kiroween 2026 — Skeleton Crew
> Deadline: Friday, December 4, 2026 at 2:00 PM PT
> Prizes: $100,000 in prizes
> Rule: New projects only — built during the Submission Period (from October 30, 2026). Anything started before October 30, 2026 is NOT eligible.
> Author note: Structure follows the 2025 winners' page shape (Problem → What it does → Two apps → Template → Kiro table → Setup). Structure only — no winner code or apps copied.

---

## Problem

California pays unemployment benefits with a very old computer system.

- The core system is called SCDB — Single Client Database.
- It is the record book for every unemployment claim and every payment in California.
- The claims core was built around 1979.
- EDD called it a "45-year-old mainframe-based claims management system" in 2024.
- It was still running in February 2026.
- A replacement (EDDNext / ICMS) is planned for June 2029.

When a system is that old, a claim can be hard to follow. A person files, then waits, and cannot see clear steps.

We do **not** claim:
- a single named oldest program — none is published
- a line count — none is published
- a COBOL version — none is published

We rebuild only from public rules. No EDD source code is used or wanted. California computer software is not public domain (Gov. Code § 7922.585).

## What it does

One skeleton. One sentence:

> **Form in → rules check → steps move → money moves → person sees a clear timeline.**

Five steps:

| Step | In | Out |
|---|---|---|
| 1. Form in | Person fills in one form | One saved record, with its own ID |
| 2. Rules check | Record + public rules | Yes / no, and an amount |
| 3. Steps move | Checked record | Record moves step by step, every step written down |
| 4. Money moves | One approved step | One payment — never two for the same item |
| 5. Timeline | Every written step | A clear timeline the person can read |

The same five steps run two different apps. That is the Skeleton Crew proof.

## Two apps, side by side

|  | App 1 — California unemployment claims | App 2 — Parking permits |
|---|---|---|
| **World** | State benefits | Campus / city parking |
| **Form** | Claim form: who they are, where they worked, what they earned | Permit application: person, car, address |
| **Rules check** | Public CA rules: CUIC § 1280 WBA table $40–$450, base period, $1,300 in highest quarter — or $900 + total ≥ 1.25× highest quarter; waiting week; partial-earnings disregard (greater of $25 or 25% ignored) | Permit rules: is the car allowed? Is the address allowed? What type and fee apply? |
| **Steps move** | Filed → Waiting week → Certified (every 2 weeks) → Paid | Applied → Checked → Approved (or Denied with reason) |
| **Money moves** | Payment for each certified week; max 26 weeks; one unpaid waiting week first | Driver pays the permit fee once, before issue |
| **Timeline** | Claim timeline: what happened, what happens next | Permit timeline: applied / checked / approved / issued |
| **Skeleton code** | The 5-step skeleton engine lives in `skeleton/skeleton.py` (class `Case`); App 1 runs on it — `claim_flow.py` supplies the claim form + `claim_rules`, with benefit math in `wba.py` / `base_period.py` | Same engine, override layer only in `app2_parking/parking.py`: new form, new rules, new labels — proof tests in both apps keep this honest |

**App 2 decision:** Settled by Jose Luis on October 30, 2026 — Parking Permits. The calculator + simulator pair as App 2 is **closed** and will not be built.

## What you get in the template

Repo assembled locally on Oct 30, 2026 (with Jose Luis's approval) — the list below is what is in it:

- The 5-step skeleton as a small, readable template
- One rules file per app — rules live in one place only
- One form definition per app
- One timeline view, reused by both apps
- Sample data for both apps (fictional people / cars only)
- Tests for the public rules (App 1) and the permit rules (App 2)
- The `/.kiro` directory at the repo root: specs, hooks, and steering docs (see KIRO-DIR-PLAN.md)
- Setup in minutes: one setup command + one run command per app (see SETUP.md)

## How we used Kiro

Honest status key: **USED** = done in this project · **DRAFT** = written as a plan/doc, not yet run in Kiro · **TO-DO** = not yet done

| Kiro feature | What we used / will use in this project | Status |
|---|---|---|
| **Vibe coding** | Fast first pass on screens and timeline view from plain-English prompts; then checked against the public rules before keeping any of it. Planned prompts are listed in the specs. | TO-DO — no Kiro session run yet at draft time (Oct 30, 2026) |
| **Agent Hooks** | Hooks at the pauses: form not finished, identity proof pending, wages missing, certification due (every 2 weeks), staff review needed, final check before money moves. For App 2: application incomplete. Real hook files are in `/.kiro/hooks/` (7 files). | DONE (files) — written as hook documents describing each pause point; not executed by the Kiro runtime in this local build |
| **Spec-driven development** | Specs written before code: claim flow, rules check (CUIC § 1280 table, base period, waiting week), certification, payment-once rule, timeline; permit flow spec for App 2. Real spec files are in `/.kiro/specs/`: skeleton-core + timeline specs, plus folder specs (requirements / design / tasks) for each app. | USED — specs preceded the code (design pack) and the code follows them |
| **Steering docs** | Plain-language rules for the build: build the 5 bones in order; keep rules in one place only; same input, same answer every time; write every step down; pay once, never twice; plain words on every screen. Real steering files are in `/.kiro/steering/` (6 files). | USED |
| **MCP** | TO-DO: evaluate MCP only if a tool is needed during the build (for example, a docs or data lookup the skeleton requires). No MCP server is claimed as used at draft time. If none is needed, this row will say "Not used — not needed" in the final submission. | TO-DO — not used yet; do not claim until actually used |

> Do not change a TO-DO or DRAFT row to "used" until the work has actually happened and can be shown in the repo / `.kiro` directory.

## Setup in minutes

See SETUP.md for the full version. Short version:

| App | Setup (once) | Run |
|---|---|---|
| App 1 — EDD claims | `python3 --version` (nothing to install — stdlib only) | `python3 app1_unemployment/demo.py` |
| App 2 — Parking permits | `python3 --version` (same check) | `python3 app2_parking/demo.py` |

- Functional app URL: **TO-DO — not yet hosted. No URL is claimed in this draft.**
- Demo video (under 3 minutes): **TO-DO — shot list only, see SETUP.md. No video exists yet.**

## Facts box (for judges)

| Item | Fact |
|---|---|
| Hackathon | Kiroween 2026 (Devpost) |
| Deadline | Friday, December 4, 2026, 2:00 PM PT |
| Prizes | $100,000 |
| Eligibility | New project, built during the Submission Period only |
| Repo rule | Public GitHub repo MUST include `/.kiro` at the root — do NOT add it to `.gitignore` |
| System rebuilt | CA EDD SCDB, claims core c. 1979; "45-year-old" in EDD's 2024 wording; still running Feb 2026; ICMS replacement Jun 2029 |
| Rules source | Public rules only — CUIC § 1280 and published EDD rules. No EDD code. |
