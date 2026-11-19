---
name: status
description: Show where a Google Ads and Microsoft Ads account stands across the paid search lifecycle - intake, plan, tracking, structure and build, launch, optimization cadence, tests and audit - each as done, needs you, waiting on data, or not set up, and which skill to run next. Use when someone asks where things stand, what's left before launch, what to do next, or opens an account they haven't seen in a while.
license: MIT
compatibility: Any Agent Skills client. Reading the account yourself needs google-ads / bingads and your own access.
metadata:
  role: paid-search-manager
  stage: status
  cadence: Any time
  summary: Every step as done / needs you / waiting on data / not set up, and the next skill to run.
  needs: Account access or a description of what exists; whether intake, plan and tracking were done
---

# Status

## Needs
Read access (or a description) and whatever exists: intake doc, plan, conversion setup, campaigns, reports, test log.

## If something is missing
Ask, step by step, rather than assuming: "Is there a signed-off intake with goals?" Unknown = "not set up", never "done".

## Method
Check each step and mark it **done**, **needs you** (a decision or approval), **waiting on data** (e.g. under 30 conversions for a target), or **not set up**:
| Step | Done when | Skill |
|---|---|---|
| Intake | goals, values, budget, step limit signed off | intake |
| Plan | forecast, split and scenarios agreed | forecast-and-budget, target-math |
| Tracking | one primary everywhere, test conversion seen on both platforms | tracking-plan |
| Structure and build | campaigns built paused and read back; parity clean | campaign-structure, negatives-and-fencing, ad-copy, pmax-and-ai-max, build, parity-check |
| Launch | client approved, enabled, read back, read dates set | launch-check |
| Daily | pacing and alerts checked | pacing-and-alerts |
| Weekly | queue reviewed, search terms, parity, tests | weekly |
| Monthly | every gap diagnosed, report sent, budget rebalanced | monthly |
| Quarterly | audit, QBR, re-plan | quarterly |
Count launch items only toward "X of Y done to launch"; optional items (CRM connection, alerts, test ideas) never block.

## Output
"X of Y done to launch", then the table with status and evidence, then the one next skill to run and why.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_status` returns every step's status; `paid_search_accounts` lists accounts.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens): `python3 scripts/run.py ads google_snapshot --out snapshot.json` (campaigns, statuses, conversions) and `python3 scripts/run.py ads google_report campaign_daily --days 30` (is it spending, how many conversions).
3. **Your own data**: whatever docs and exports exist; walk the table with the person.
