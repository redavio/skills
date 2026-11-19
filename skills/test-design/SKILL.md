---
name: test-design
description: Design paid search experiments for Google Ads and Microsoft Ads - pick the next test from a ranked idea bank (ICE scoring, standard test library), write the hypothesis and goal metric, size it in clicks per arm, set the read date in whole weeks, and set up a 50/50 platform experiment with one variable. Use when someone asks what to test next, how long a test needs, how to set up an AI Max, bidding, ad copy or landing page test, or to build a test backlog.
license: MIT
compatibility: Any Agent Skills client. Sizing and ICE math need Python 3.10+, standard library only.
metadata:
  role: paid-search-lead
  stage: run
  summary: Ranked idea bank, hypothesis card, clicks per arm and a read date, 50/50 with one variable.
  needs: Test ideas (or use the standard library); the goal metric; baseline conversion rate and weekly clicks for the campaign tested
---

# Test design

## Needs
Ideas (or start from the standard library below), the campaign's goal metric, its baseline conversion
rate, weekly clicks, and the smallest lift worth detecting.

## If something is missing
No ideas: load the standard library. No baseline: pull the last 28 days. Ask what lift would change a decision (default 20% relative).

## Method
1. **Idea bank, four sources**: the standard library (every account), brainstorms, research (platform announcements, competitor ads, your own data), and attributes that correlate with results (copy, pages, terms; tested, never applied directly).
2. **Standard library**: AI Max on Non-brand (then Brand and Competitor once it proves out); Search partners on; target impression share on Brand; Smart Bidding Exploration on tROAS (tolerance 5-30%); Journey-Aware Bidding (tCPA path) vs the value path; Microsoft broad match + LinkedIn targeting on named companies and roles; an ad copy test in every main ad group; one-time brand holdout.
3. **One card per idea**: hypothesis, goal metric (as deep in the funnel as data is reliable), source, ICE (impact = volume affected x expected lift; confidence = own past test > platform data > industry data > gut; ease = effort; risk flagged separately), 1-10 each. A person approves an idea into the backlog.
4. **Size it**: clicks per arm to detect the lift at 95% confidence and 80% power; read date = whole weeks at current volume. Too long (over ~12 weeks)? Test a bigger change, a higher-volume campaign, or a shallower metric.
5. **Run it**: the platform's experiment tool, 50/50 split, one variable, no changes mid-test. AI Max = experiment on the live base, never a second live copy. Incrementality questions (brand, big spend) = holdouts or geo tests judged on CRM pipeline.
6. Track velocity: tests launched per month, win rate, cumulative impact.

## Output
The ranked backlog (ICE), then the chosen test's card: hypothesis, variable, goal metric, split, clicks per
arm, read date, what counts as a win, risks. Setting up the experiment is a change the person approves.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_performance` gives baseline rate and volume; `paid_search_proposals` can queue the experiment for approval.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py perfos test-size --baseline-cvr 0.04 --min-lift 0.2 --weekly-clicks 1800
   python3 scripts/run.py perfos ice --input ideas.json      # [{"hypothesis": "...", "impact": 7, "confidence": 5, "ease": 8}]
   python3 scripts/run.py ads google_report campaign_daily --days 28
   ```
3. **Your own data**: an experiment database sheet with the card fields; paste baseline numbers in chat.
