---
name: expansion-finder
description: Find where to grow a Google Ads or Microsoft Ads account - micro expansion inside the existing structure (new keywords from converting search terms, ad variants, audience segments, locations, a new competitor ad group) and macro expansion that needs a new campaign, budget or goal (a theme that outgrew its campaign, a new product, market or language), with headroom from impression share. Use when someone asks how to scale paid search, where to spend more, or what to add next.
license: MIT
compatibility: Any Agent Skills client. Math needs Python 3.10+, standard library only.
metadata:
  role: paid-search-lead
  stage: run
  summary: Micro adds from your own data; macro proposals when a theme outgrows its home, launched as tests.
  needs: Ad group and search term performance (13 weeks is best); impression share lost to budget and rank; goals; new products or markets planned
---

# Expansion finder

## Needs
Ad group cost and conversions over ~13 weeks, converting search terms, impression share (lost to budget
and rank), goals, and any planned products, markets or languages.

## If something is missing
Ask whether any new product, market or competitor is coming: those are macro triggers you can't see in the data.

## Method
1. **Micro or macro**: does it need a new campaign, budget or goal? No = micro. Yes = macro.
2. **Micro** (from your own data, through the volume gate): promoted search terms as exact keywords; ad variants; audience segments; location changes; a new competitor name in the existing Competitor campaign. Part of weekly optimization.
3. **Headroom**: impression share lost to budget on campaigns beating target = more budget (budget-rebalance). Lost to rank = ads, landing pages or bids, not budget.
4. **Macro triggers**: quarterly planning; a new product or program; a market or competitor shift; a theme that outgrew its home (default: an ad group with 50%+ of its campaign's spend and 30+ conversions in 13 weeks, in a campaign with 2+ ad groups).
5. **Macro rules**: built through the normal build (structure, fencing, copy, pages); client signs off goals, budget and positioning; launches as a test with a defined read date.
6. Every split thins smart-bidding data: only split what can stand alone.

## Output
Two lists: micro adds (item, evidence, proposed change) and macro proposals (what, trigger, evidence,
budget and goal needed, read date). Proposals only.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_proposals` (promotes and expansion), `paid_search_performance` (impression share).
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_report ad_groups --days 91 --out adgroups.csv
   python3 scripts/run.py perfos expansion --csv adgroups.csv
   python3 scripts/run.py ads google_report campaign_daily --days 28     # impression share lost to budget / rank
   ```
3. **Your own data**: ad group and search term exports with cost and conversions.
