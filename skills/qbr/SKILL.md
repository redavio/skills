---
name: qbr
description: Prepare a quarterly business review and re-plan for a Google Ads and Microsoft Ads program - quarter performance vs goals and vs last quarter, the audit compared with last quarter, tests run and their results, the ICE back-test, spend scenarios with headroom, macro expansion, benchmark refresh, revisiting estimated intake values, and the next-quarter plan and budget. Use when someone asks for a QBR, quarterly review, quarterly plan, or next quarter's paid search budget.
license: MIT
compatibility: Any Agent Skills client. Math needs Python 3.10+, standard library only.
metadata:
  role: paid-search-manager
  stage: review
  cadence: Quarterly
  summary: Quarter vs goals and last quarter, tests and learning, scenarios, and the next-quarter plan for sign-off.
  needs: The quarter's and last quarter's performance (and pipeline); goals; the test log; last quarter's audit; next quarter's goal or budget
---

# QBR

## Needs
This and last quarter's performance by row (brand, non-brand, PMax, Google, Microsoft) with pipeline,
goals, the test log, last quarter's audit, next quarter's goal or budget, and which intake values were estimates.

## If something is missing
No last-quarter audit: run the audit now and compare next time. No test log: list tests from the change history and mark results unknown.

## Method
1. **Report**: the exec-report table for the quarter vs goal and vs last quarter, with driver sentences (diagnose) for every gap.
2. **Audit vs last quarter**: setup health then and now, findings closed and new.
3. **Tests**: what ran, results at 95% confidence, decisions, cumulative impact, velocity (tests per month). **ICE back-test**: did top-third ICE ideas win more often than the rest? Adjust the scoring.
4. **Spend scenarios** (Base, +20%, +50%): headroom from impression share and demand ceilings; extra spend buys results at a higher cost than today's average, shown as a range.
5. **Re-plan**: budget shifts on pipeline ROAS (cost per opportunity as the early signal); Brand stays budgeted for impression share and the holdout result, never moved on ROAS alone. Microsoft scales toward 20-30% if its cost per opportunity holds.
6. **Revisit estimates**: intake values marked Estimate get replaced with real data (stage rates, values, conversion lag); rerun target-math.
7. **Macro expansion and benchmarks**: themes that outgrew their campaign, new products or markets; refresh benchmarks (own history first, similar accounts next, external as a sanity check within the same industry).
8. **Next quarter**: goals, budget split, 30/60/90 roadmap, top tests, risks, sign-off.

## Output
A deck outline: 1 TL;DR, 2 performance vs goals, 3 why (drivers), 4 audit change, 5 tests and learning,
6 scenarios, 7 next-quarter plan and budget, 8 decisions needed. Offer to build it in their slide tool.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_performance`, `paid_search_diagnose`, `paid_search_audit`, `paid_search_test_read`, `paid_search_forecast` (scenarios).
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_report campaign_daily --days 182 --out half.csv
   python3 scripts/run.py perfos report --facts half.csv --start 2026-08-01 --end 2026-10-31 
   python3 scripts/run.py perfos ice --input tests.json
   python3 scripts/run.py perfos forecast --input plan_inputs.json
   ```
   (For the comparison quarter, run `perfos report` again with last quarter's dates.)
3. **Your own data**: quarterly exports, the CRM pipeline report and the test log sheet.
