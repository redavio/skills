---
name: forecast-and-budget
description: Build a directional paid search plan for Google Ads and Microsoft Ads - a full-funnel forecast from keyword volume (searches, clicks, cost, every conversion stage with CPA and ROAS), the starting budget split across Brand, Non-brand, Competitor, Performance Max and Google vs Microsoft, and Base / Medium / High spend scenarios capped by demand. Use when someone asks how much to spend on paid search, how to split budget, what results a budget will buy, for a media plan, or spend scenarios.
license: MIT
compatibility: Any Agent Skills client. The math needs Python 3.10+, standard library only.
metadata:
  role: paid-search-lead
  stage: set-up
  summary: Funnel forecast, starting budget split and spend scenarios; a directional guide, never a verdict.
  needs: Monthly budget (or a pipeline goal and pipeline per dollar); keywords with volume and CPC (or placeholders); conversion points with values; goals
---

# Forecast and budget

The plan is a directional guide for leadership, never a verdict. Forecasts often miss: show the
variance against the goals and use it to steer, but never read a low forecast as "this won't work".
Brand and non-brand are always separate line items: brand is cheap and converts well but mostly
captures demand created elsewhere, so blending it in skews every number.

## Needs
- Monthly budget, or back into it: pipeline goal / pipeline per dollar from their CRM history.
- Keywords with monthly searches and CPC per campaign type and platform (keyword-research).
- Conversion points in funnel order with agreed values (lead, MQL, SQL, opportunity, closed won).
- Goals per conversion point (monthly).

## If something is missing
Ask for the budget or the goal first. Every other number has a labelled default: say which defaults
you used. Missing conversion rates use placeholders (click to first conversion 3%, each later step
10%) until their own history replaces them: ask "Do you know your demo-to-opportunity rate?".

## Method
1. **Forecast per platform and campaign type**: searches x share we show for (placeholder: brand 90%, non-brand 50%, competitor 30%) = impressions; x click rate (brand 30%, non-brand 4%, competitor 3%) = clicks; x CPC (platform estimate, else Google's borrowed for Microsoft, else placeholder) = cost; then each conversion point with its volume, CPA and ROAS. Stages a client doesn't use are greyed and skipped. Every assumption carries its source: their data, benchmark or placeholder.
2. **Starting split**:
   - Microsoft takes its share off the top: start at 10-15% of search budget, own budget and targets; scale toward 20-30% if its cost per qualified lead holds up. Never a fixed share of Google.
   - Brand: what ~90% impression share of brand searches costs, never below a floor. Budget for coverage, not ROAS. A one-time brand holdout test learns its real incremental value.
   - PMax: a test share (default 10% of what's left), from day one, with a read date.
   - Non-brand and Competitor share the rest as one pool (competitor shown as its own line so its cost doesn't hide).
   - No campaign below the minimum daily budget; the pool pays for raising anything up. If the minimums alone don't fit, say so.
   - Daily = monthly / 30.4. A person can type over any daily budget; the pool absorbs the difference.
3. **Scenarios**: Base, Medium (+20%), High (+50%). Each line spends only up to its demand ceiling (all its searches); extra budget past that is "capped by demand". PMax has no keyword demand: its spend shows as "not forecast". Extra spend buys results at a higher cost than today's average.
4. **Template**: goals, demand sizing, budget build, split, scenarios, 30/60/90-day roadmap, risks, sign-off. Re-plan quarterly and when ACV, win rate or stage rates change; then budget shifts on pipeline ROAS (cost per opportunity is the early signal). Brand budget never moves on ROAS alone.

## Output
1. Forecast table: platform, campaign type, searches, clicks, CPC (source), cost, then each conversion point's volume and CPA, total row.
2. Budget split: platform, campaign type, monthly, daily, flags (at minimum, set by you, minimums exceed budget).
3. Scenarios next to the goals: spend forecast, not forecast, each stage's volume vs goal, capped lines.
4. Assumptions with sources. One line on top: "Directional guide, not a verdict."

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_forecast` returns the forecast, split and scenarios from the account's intake and keyword research.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens): pull keyword ideas (keyword-research skill), then run the math:
   ```
   python3 scripts/run.py perfos forecast --input plan_inputs.json
   ```
   `plan_inputs.json`: `{"keywords": [{"keyword": "agency crm", "campaign_type": "nonbrand", "platform": "google", "monthly_searches": 2400, "low_cpc": 6, "high_cpc": 14}], "points": [{"name": "Demo request", "value": 400}, {"name": "Opportunity", "value": 6000}], "monthly_budget": 15000, "goals": {"Opportunity": 20}, "assumptions": {"rate_to_first": 2.5, "split:microsoft": 15}, "daily_overrides": {"google:brand": 40}}`. Percentages are whole numbers (15 = 15%).
3. **Your own data**: a keyword export plus their funnel numbers in a sheet; the same JSON can be built from it, or paste the numbers in chat.
