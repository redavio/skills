---
name: quarterly
description: The quarterly paid search loop for Google Ads and Microsoft Ads - runs audit (compared with last quarter), qbr (report, tests, spend scenarios, next-quarter plan), expansion-finder for macro expansion, the ICE back-test, forecast-and-budget to re-plan, and target-math with real data replacing estimates, in that order. Use for a quarterly review, QBR prep, or quarterly re-plan; also when an engagement ends (then run handoff).
license: MIT
compatibility: Any Agent Skills client. Uses the job skills it calls.
metadata:
  role: paid-search-manager
  stage: cadence
  cadence: Quarterly
  summary: "Once a quarter: audit, QBR, expansion, back-test, re-plan, refresh estimates."
  needs: Account access; this and last quarter's data and pipeline; the test log; next quarter's goals or budget
---

# Quarterly

## Needs
Account access, this and last quarter's data (with pipeline if available), last quarter's audit, the test log, next quarter's goals or budget. Missing pieces: ask in chat.

## Steps
1. **audit**, compared with last quarter.
2. **qbr**: the report, tests and learning, spend scenarios, next-quarter plan, in deck form.
3. **expansion-finder**: macro expansion (themes that outgrew their campaign, new products, markets, competitors); refresh benchmarks.
4. **test-read** back-test: do high ICE scores win more? Adjust scoring.
5. **forecast-and-budget**: re-plan on pipeline ROAS; Brand on impression share and holdout.
6. **target-math**: replace values agreed as estimates with real data.
7. Engagement ending? Run **handoff**.

## Output
The audit, the QBR deck outline and the signed-off next-quarter plan.

## Getting the data
(1) Redavio connector at `https://app.redavio.com/mcp` (`paid_search_audit`, `paid_search_performance`, `paid_search_test_read`, `paid_search_forecast`, `paid_search_target_math`); (2) your own API access (Google Ads and Microsoft Advertising developer tokens plus your own OAuth app credentials for each; mode 1 needs none) with each job skill's scripts; (3) your own data.
