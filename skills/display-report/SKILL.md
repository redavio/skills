---
name: display-report
description: The one scorecard for Google Demand Gen and Microsoft Audience ads, the same for every campaign and platform, in order - cost to reach (CPM and frequency against a benchmark band), brand lift (branded search and direct traffic moving with display spend, lag shown), and pipeline from target accounts (Account Hub with HubSpot). Engaged views, accounts reached and click conversions are supporting detail; view-through is always labelled and never scored. Use for the weekly or monthly display report, or when asked whether display or YouTube is working.
license: MIT
compatibility: Any Agent Skills client. Math needs Python 3.10+, standard library only.
metadata:
  role: paid-display-manager
  stage: review
  cadence: Weekly and monthly
  summary: "One scorecard for every display campaign: cost to reach, brand lift, pipeline."
  needs: Weekly display cost, impressions and reach; weekly branded searches and direct visits; a CPM benchmark band; HubSpot (Account Hub) for pipeline
---

# Display report

## Needs
Weekly display cost, impressions and reach (8+ weeks for brand lift), weekly branded searches and direct
visits, the CPM benchmark band, and pipeline from target accounts when HubSpot is connected.

## If something is missing
Fewer than 8 weeks: report cost to reach and say brand lift needs more weeks. No HubSpot: say "connect
HubSpot" on the pipeline line; never estimate pipeline.

## Method
1. **Cost to reach**: CPM against the band and weekly frequency (`display-scorecard`).
2. **Brand lift**: correlation of weekly display spend with branded searches and direct visits, at the best lag of 0 to 3 weeks. It's correlation; a holdout (lift-test) proves it.
3. **Pipeline**: pipeline from target accounts reached, from Account Hub.
4. **Supporting detail, never scored**: engaged views, share of the target account list reached (Microsoft Professional Demographics; Google Customer Match reach), click conversions, view-through (labelled).
5. **One line**: the scorecard in a sentence, then what to do next (display-review proposals, or a lift-test).

## Output
The three lines in order with status, then supporting detail, then the one-line read.

## Getting the data
1. **Redavio connector**: `paid_display_scorecard` (reads display spend, reach and branded search from the account; pipeline through Account Hub).
2. **Your own API access**:
   ```
   python3 scripts/run.py ads google_report dg_reach --days 56
   python3 scripts/run.py ads microsoft_report professional_demographics --days 28
   python3 scripts/run.py perfos display-scorecard --input weeks.json --cpm-low 5 --cpm-high 15 --pipeline pipeline.json
   ```
