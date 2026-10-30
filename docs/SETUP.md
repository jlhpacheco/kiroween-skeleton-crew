# Setup — verified against the real repo (Oct 30, 2026)

> **Status: VERIFIED.** Every command below was run in this repo on Oct 30, 2026 and produced the stated result.
> This replaces the earlier Track D draft, which used placeholder entry names (`app1_claims.py`, `app2_permits.py`, a `requirements.txt` that does not exist). The real build is **pure Python standard library — there are no dependencies and no `requirements.txt`**.

## One setup command + one run command per app

### Setup (once — same for both apps)

There is nothing to install. Setup is one check that Python 3 is present:

```bash
python3 --version
```

Verified result: `Python 3.12.3`.

### App 1 — California unemployment claims

Run:

```bash
python3 app1_unemployment/demo.py
```

Verified result (exit 0): claim dated Nov 2, 2026; highest quarter $5,200 → WBA $200; waiting week pays $0; week 2 with $200 earnings pays $50; **total paid $450.00**.

### App 2 — Parking permits

Run:

```bash
python3 app2_parking/demo.py
```

Verified result (exit 0): 3 cases — resident approved and paid ($30), visitor denied (address zone "Airport" is not in the allowed zones; plain reason printed, no money taken), employee exempt ($0); **payments in the ledger: 1**.

## Tests (48 total, all passing)

```bash
cd skeleton && python3 -m unittest test_skeleton -v && cd ..
cd app1_unemployment && python3 -m unittest discover -s tests -v && cd ..
cd app2_parking && python3 -m unittest discover -s tests -v && cd ..
```

Verified: skeleton 10/10 · App 1 25/25 · App 2 13/13 — **48/48 OK**.

## Functional app URL

**Not hosted — no URL is claimed.**

- Hosting is a publishing step and waits for Jose Luis's explicit approval.
- When hosting is approved and live, add here: the URL, which app it serves (App 1 / App 2 / both), and the date it was last checked working.

## Demo video — shot list only (under 3 minutes)

**Status: SHOT LIST ONLY — no video exists yet. No recording or upload is authorized yet.**

Total planned time: **165 seconds** (under the 180-second limit).

| Shot | Time | What the camera shows | Words on screen / spoken |
|---|---|---|---|
| 1 | 0:00–0:25 (25s) | The problem: title card + the 5-step skeleton diagram | "A 45-year-old claims system (in 2024). One skeleton. Two apps." Show: SCDB c. 1979, still running Feb 2026, replacement Jun 2029. |
| 2 | 0:25–1:05 (40s) | App 1 live: `python3 app1_unemployment/demo.py` — claim → rules result ($200 WBA) → waiting week → certify → timeline | "Form in. Rules check. Steps move. Money moves. Clear timeline." |
| 3 | 1:05–1:40 (35s) | App 2 live: `python3 app2_parking/demo.py` — 3 permit cases | "Same 5 steps. A different world: parking permits." |
| 4 | 1:40–2:20 (40s) | Side by side: both timelines + the template files + the `/.kiro` folder (specs, hooks, steering) | "What you get: the skeleton, both apps, and the Kiro files at the repo root." |
| 5 | 2:20–2:45 (25s) | Setup in minutes: run the setup check + one run command per app | "One setup command. One run command. Per app." End card: repo link — add only when the repo is public with approval. |

Video rules to keep:
- Under 3 minutes — hard limit.
- Show the real apps running, not slides only.
- Fictional sample data only — no real person's claim or plate.
- Do not record or upload until Jose Luis approves it.
