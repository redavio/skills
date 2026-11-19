---
name: diagnose
description: Explain why a paid search result moved versus goal or a prior period on Google Ads or Microsoft Ads - rule out tracking, split mix vs rate across Brand, Non-brand and PMax, then a Shapley split of the gap across levers (CPC, CTR, conversion rate, funnel stage rates, deal value) that adds to 100%, ending in one sentence and the lever to pull. Works for CPA, ROAS, conversions, conversion value, cost per opportunity, pipeline and closed-won. Use when someone asks why CPA went up, why conversions dropped, why ROAS fell, or what drove a change.
license: MIT
compatibility: Any Agent Skills client. Math needs Python 3.10+, standard library only.
metadata:
  role: paid-search-lead
  stage: review
  summary: Why a KPI moved: tracking first, mix vs rate, then a fair lever split and the one lever to pull.
  needs: Totals for the period and the comparison (goal or prior period): impressions, clicks, cost, conversions, value, and funnel stage counts if diagnosing past the platform; the same by segment for the mix check
---

# Diagnose

## Needs
Volume totals for the period and the base (the paced goal, or an equal prior period with the same
weekdays, or last year for seasonality): impressions, clicks, cost, conversions, conversion value; MQLs,
SQLs, opportunities, pipeline, won value if going past the platform. The same per segment for the mix check.

## If something is missing
No goal for every lever? Use the prior period as the base and say so. Missing CRM stages? Diagnose to the
platform conversion and note the funnel stops there.

## Method
1. **Rule out tracking first**: conversion tags, offline imports, the change log. If the CRM held and the platform moved, it's tracking or attribution, not performance. Stop there.
2. **Mix check**: did the total move because spend shifted between segments (brand, non-brand, PMax, Google vs Microsoft) or because segments got better or worse? Mostly mix = a budget or targeting question. Mostly rate = step 3.
3. **Lever split with Shapley** (fair split, shares add to 100%, no order bias, handles zeros). Split on levers, never outcomes (cost and conversions are outcomes):
   - Conversions = impressions x CTR x conversion rate
   - CPA = CPC / conversion rate
   - ROAS = value per conversion x conversion rate / CPC
   - Cost per opportunity = CPC / (conversion rate x conv-to-MQL x MQL-to-SQL x SQL-to-opportunity)
   - Full funnel: impressions x CTR x each stage rate x deal value (stages are config: drop the ones they don't use)
4. **Volume gate**: don't blame a lever whose denominator is too thin (e.g. a stage rate on 4 SQLs). Show the number; don't name it as the driver.
5. **Act**: end with the lever to pull and the next test. CTR or conversion-rate drivers -> look at the copy or landing pages behind them and turn findings into tests, not direct changes. CPC driver -> auction insights, Quality Score, bidding changes in the change log.
6. Cadence: weekly on the biggest movers; monthly on every gap to goal; in audits and QBRs.

## Output
One sentence first: "CPA 18% over goal: click to conversion rate drove 72%." Then the lever table (lever,
base, actual, contribution, share, low-volume flag), the mix result, what was ruled out, and the next action.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_diagnose` runs all three steps; `paid_search_performance` for the totals.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_report campaign_daily --days 56 --out daily.csv
   python3 scripts/run.py perfos diagnose --kpi cpa --actual '{"cost": 5500, "clicks": 2500, "conversions": 100}' --base '{"cost": 5000, "clicks": 2500, "conversions": 125}' --vs prior --min-volume '{"clicks": 60}'
   python3 scripts/run.py perfos mix --kpi cpa --actual '{"brand": {"cost": 900, "conversions": 60}, "nonbrand": {"cost": 4600, "conversions": 40}}' --base '{"brand": {"cost": 1000, "conversions": 70}, "nonbrand": {"cost": 4000, "conversions": 55}}'
   ```
   KPIs: conversions, cpa, roas, s2s, pipeline, won, won_value, cost_per_s2, cost_per_won, pipeline_roas, won_roas; or a custom chain with `--factors`.
3. **Your own data**: two periods' totals from any export or CRM report, pasted in chat.
