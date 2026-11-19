---
name: prune-promote
description: Judge every paid search lever against goal with the volume gate - keywords, match types, search terms, PMax search themes, audiences, locations, devices, hours, days of week, networks, placements, ads and landing pages - and turn the verdicts into a proposed change list (pause, exclude, add negative, graduate to exact, raise bid) for Google Ads and Microsoft Ads. Use for weekly optimization, finding wasted spend, deciding what to pause or scale, or building an approval queue.
license: MIT
compatibility: Any Agent Skills client. Math needs Python 3.10+, standard library only.
metadata:
  role: paid-search-lead
  stage: run
  summary: Every lever judged the same way against goal; cuts and promotes become a change list for approval.
  needs: Daily or weekly performance by lever (clicks, conversions, cost, value); goal conversion rate and target CPA or ROAS per segment
---

# Prune or promote

Is this lever pulling its weight? Every dimension is judged the same way: performance vs goal, with the
volume gate deciding whether there's enough data. Dimensions are what we review; metrics are how we judge them.

## Needs
Performance by lever over whole weeks, with segment (brand / non-brand / PMax); the goal conversion rate
and target per segment (CPA, ROAS, or none for conversions / value goals).

## If something is missing
Ask for each segment's goal. Never borrow brand's goal for non-brand.

## Method
1. **Primary test**: performance vs goal through the volume gate (cut past the click line and below goal; promote at 3+ conversions beating target; flag 2x target CPA with no conversions; else watch). Whole weeks, 7-day minimum, extend a week at a time.
2. **Context**: trend and benchmark. Below goal but improving = hold, not remove. Near goal = hold.
3. **What each verdict means:**
   | Lever | Cut | Promote |
   |---|---|---|
   | Search term | negative (phrase; exact for a head term) | exact keyword in the right ad group |
   | Keyword | pause | graduate to exact / more budget |
   | Match type | tighten | - |
   | PMax search theme | remove | - |
   | Audience | exclude | bid up (observation) |
   | Location | exclude | bid up (Microsoft respects it) |
   | Device | exclude only a clear dead zone | - |
   | Hour / day | exclude a dead zone (real spend, zero conversions) | - |
   | Placement / network | exclusion list / review setting | - |
   | Ad / asset | pause or rewrite (as a test) | keep, write more like it |
   | Landing page | test a new page | - |
4. **Under smart bidding** Google ignores bid adjustments except -100%; only full exclusions are levers there.
5. **Before cutting**: pool thin items by theme in the same campaign type; rule out tracking breaks and conversion lag.
6. **Hero campaigns** (graduating winners to their own exact campaign): only with enough volume to stand alone; add the term as an exact negative in the source campaign.
7. **Quality Score** components are a diagnostic for keywords below goal, never a goal.

## Output
The change list: lever, item, campaign, verdict, proposed change, evidence (clicks vs line, CPA or ROAS
vs target, window), safety level. Cuts and promotes first, flags after. Proposals only.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_proposals` returns the queue across every lever; `paid_search_volume_gate` for one lever.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_report keywords --days 28 --out kw.csv
   python3 scripts/run.py perfos terms --csv kw.csv --name-col keyword --level keyword --goals goals.json
   python3 scripts/run.py ads google_report by --dimension hour --days 56 --out hours.csv
   python3 scripts/run.py perfos terms --csv hours.csv --name-col hour --level hour --goals goals.json
   ```
3. **Your own data**: any export with a name column and clicks, conversions, cost (and segment).
