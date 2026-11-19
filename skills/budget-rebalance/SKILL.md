---
name: budget-rebalance
description: Recommend daily budget changes for Google Ads and Microsoft Ads campaigns on marginal return - raise budget-capped winners up to recoverable impression share, trim campaigns missing CPA or ROAS goals, cut money-burners, keep Brand budgeted for impression share - with adaptive significance windows, volatility dampening and a step limit. Use when someone asks where to move budget, which campaigns deserve more or less spend, or for a monthly budget rebalance.
license: MIT
compatibility: Any Agent Skills client. Math needs Python 3.10+, standard library only.
metadata:
  role: paid-search-lead
  stage: run
  summary: Budget moves per campaign on performance vs target and recoverable impression share, within the step limit.
  needs: Daily cost, conversions (and value or funnel stages) per campaign; current daily budgets; impression share and share lost to budget; target per campaign; last budget change dates; the step limit
---

# Budget rebalance

Recommendations only. Moves within the step limit are routine; bigger ones need the client too.

## Needs
Per campaign: current daily budget, target (CPA, ROAS or a funnel objective like cost per opportunity),
daily cost and conversions (value or stage counts for value objectives) for up to 90 days, search
impression share and share lost to budget, the date of the last budget change. The client's step limit.

## If something is missing
No impression share data: no increases can be sized (say so); decreases still work. No target: ask; never infer one.

## Method
1. **Brand is not budgeted on return**: it's budgeted for ~90% impression share. Below that = raise; never cut Brand on ROAS (it always looks great).
2. **Window**: expand back from yesterday until enough conversions (default 10 of the objective's events), at least 7 days, never past the last budget change (data straddling a change is dirty).
3. **Increase** only for a campaign beating target AND losing 10%+ impression share to budget. Size it by recoverable share (lost to budget / impression share), dampened for volatility, capped at the max change (default 20%). Not budget-limited = no increase (more budget won't buy more).
4. **Decrease** for campaigns missing target: 10-30% off target -> about 10%; 30%+ -> about 20%; dampened for volatility, capped.
5. **Cut lane**: a campaign spending its full budget for 7+ days at 2x+ the target CPA (or under half the target ROAS), or with zero return, can be cut even below the conversion gate. With medium+ confidence (or zero return) it's cut to 25% of average daily spend, past the normal cap.
6. Skip shared budgets, paused campaigns, moves under 3%, and anything outside min/max budget guards.
7. Re-plan quarterly on pipeline ROAS; cost per opportunity is the early signal.

## Output
Table: campaign, segment, current daily, recommended daily, change %, objective actual vs target, window
(days, events), confidence, reason (above target / below target / inefficient spend / egregious cut),
safety level vs the step limit. Brand lines with their impression-share check. Proposals only.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_proposals` includes budget moves; `paid_search_performance` gives the inputs.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_report campaign_daily --days 90 --out daily.csv
   python3 scripts/run.py perfos rebalance --input rebalance.json
   ```
   `rebalance.json`: `{"config": {"objective": "cpa", "higher_is_better": false, "significance_metric": "conversions"}, "campaigns": [{"campaign_id": "1", "name": "search|nonbrand|crm|us|en", "segment": "nonbrand", "current_budget": 100, "target": 250, "lost_is_budget": 0.3, "impression_share": 0.5, "last_change": "2026-10-01", "daily": {"2026-11-01": {"cost": 98, "clicks": 40, "conversions": 1}}}]}`. For ROAS: `"objective": "roas", "higher_is_better": true` and `conversion_value` in daily. Apply an approved move: `ads google_apply budget --campaign C --daily 115` (dry run, `--live` after a yes).
3. **Your own data**: a daily campaign export with budget and impression share columns.
