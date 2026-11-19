---
name: volume-gate
description: Decide whether a paid search keyword, search term, audience, location, device, hour, placement, ad or landing page has enough clicks to judge against goal, using a click-based rule of three (95% confidence). Works for CPA, ROAS, conversions and conversion value goals. Use when someone asks if they have enough data to cut, pause, exclude or scale something, how long to wait, or whether a result is just noise.
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only.
metadata:
  role: paid-search-manager
  stage: run
  summary: How many clicks before calling a keyword, term or any other lever: cut, promote, flag or watch.
  needs: Clicks, conversions and cost for the item (whole weeks); the goal conversion rate; the target CPA or target ROAS if there is one
---

# Volume gate

The gate is clicks-based, so a dud can't burn budget waiting for a conversion that never comes.
It answers one question for any lever: is there enough data to act, and if so, which way?

## Needs
- For the item: clicks, conversions, cost (and conversion value for value goals), over whole weeks.
- The goal conversion rate for its segment (brand and non-brand have their own).
- The target it's judged on: target CPA, target ROAS, or none (conversions or conversion value goals).

## If something is missing
Ask in chat: "What conversion rate counts as on goal here?" If they don't know, offer their own
last-90-day rate for that segment and label it. For a ROAS goal with no CPA, ask for the average
value per conversion so the flag can be worked out. Never guess a goal.

## Method
1. **The line.** Cut when clicks pass the line and the item is still below goal:
   | Conversions so far | Clicks line |
   |---|---|
   | 0 | 3 / goal CVR |
   | 1 | 5 / goal CVR |
   | 2 | 7 / goal CVR |
   | 3 | 9 / goal CVR |
   | 4+ | exact 95% Poisson upper bound / goal CVR (4 conversions: 9.15 / goal CVR) |
   At a 5% goal: 60, 100, 140, 180 clicks. Past the line and still below goal = 95% sure it's worse than goal.
2. **Promote**: 3+ conversions, conversion rate at or above goal, and beating the target (CPA at or under it, or ROAS at or over it; with no target, the conversion rate alone).
3. **Flag (view only)**: 2x the target CPA spent with zero conversions, even mid-week. ROAS goal: target CPA = value per conversion / target ROAS. A flag is a look-now, not an action.
4. **Watch** everything else. Say how many clicks are still needed.
5. **Windows**: whole weeks, 7 days minimum, so day-of-week swings cancel out. If the line isn't reached, extend a week at a time (up to 13 weeks).
6. **Before acting on a cut**: pool thin items by theme within the same campaign type; rule out tracking breaks and conversion lag; use the segment's own goal (never blend brand and non-brand).
7. The same gate applies per funnel stage when judging deeper conversions (MQL, SQL, opportunity): use that stage's goal rate and count.

## Output
For each item: verdict (cut / promote / flag / watch), clicks vs the line, the window used, and one
line of why. Example: "Cut: 0 conversions on 82 clicks; past the 75-click line for a 4% goal (28 days)."
Proposals only; the person approves any change.

## Getting the data
1. **Redavio connector** (Claude or any MCP client): add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_volume_gate` runs the gate on any lever; `paid_search_performance` gives the numbers.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py perfos gate --clicks 82 --conversions 0 --cost 410 --goal-cvr 0.04 --target-cpa 250
   python3 scripts/run.py ads google_report by --dimension device --days 28 --out devices.csv
   python3 scripts/run.py perfos terms --csv devices.csv --name-col device --level device --goal-cvr 0.04 --target-cpa 250
   ```
   ROAS goal: `--target-roas 4 --value-per-conversion 900` instead of `--target-cpa`.
3. **Your own data**: any CSV or Google Sheet with a name column plus `clicks, conversions, cost` (optional `date`, `segment`, `conversion_value`); run `perfos terms` on it, or paste the numbers in chat.
