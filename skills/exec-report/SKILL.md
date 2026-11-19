---
name: exec-report
description: Write the paid search executive report for Google Ads and Microsoft Ads - a TL;DR, then one table with rows for Search brand, non-brand (competitor as a sub-row), PMax, total, Google and Microsoft, columns for spend, conversions, CPA or ROAS, opportunities, pipeline and impression share, each cell vs goal and vs prior period, a one-line driver per row, fix and press actions, and initiatives. Weekly or monthly. Use when someone asks for a paid search report, weekly update, monthly report or performance summary for leadership.
license: MIT
compatibility: Any Agent Skills client. Report math needs Python 3.10+, standard library only.
metadata:
  role: paid-search-manager
  stage: review
  cadence: Weekly and monthly
  summary: Pipeline first, brand and non-brand apart, every number vs goal with the reason behind it.
  needs: Daily performance by campaign for the period and comparison; goals per row; CRM stages and pipeline if available; what was done and what's next
---

# Exec report

One report, three rhythms: daily internal (look, don't act), weekly exec (report + status), monthly or
quarterly exec (report + tests, scenarios, next plan; see qbr).

## Needs
Daily campaign performance for the period and the comparison period, goals per row (full-period; volume
goals are paced), CRM stages and pipeline by campaign if available, what was done this period and what's next.

## If something is missing
No CRM data: report to the platform conversion and say pipeline isn't connected. No goals: compare to prior period only and ask for goals.

## Method
1. **Period**: last 28 days vs prior 28 is the main trend (last 7 days is pacing only, too noisy for B2B). Also MTD, QTD, last 13 weeks. Print the exact dates at the top; no unlabeled periods.
2. **Rows**: Search brand, Search non-brand (sub-row: competitor), PMax, Total, then Google and Microsoft under Total (always shown so a strong Microsoft isn't buried). Campaigns that don't follow the naming convention land in "unclassified": fix the names.
3. **Columns**: spend, conversions, CPA (or ROAS for value goals), opportunities, cost per opportunity, pipeline, pipeline ROAS, impression share. Each cell: value, then vs goal (paced) and vs prior in small text.
4. **Driver**: one sentence per row from the diagnose skill naming the biggest lever and its share.
5. **TL;DR**: 3 bullets: performance, why, what's next, written from the table and driver sentences.
6. **Actions**: fix (what's behind) and press (what's working). **Initiatives**: in flight and slated. **Weekly status**: what we did, what's next, decisions needed.
7. **Brand caveat**: brand conversions overstate incremental impact; read brand as protection, not growth.
8. Reconciliation of platform vs CRM is on a cohort (click date) basis; funnel stages are reported by calendar date. State the attribution model used.

## Output
Dates line, TL;DR bullets, the table, actions (fix / press), initiatives, decisions needed. Plain words,
no jargon. Offer to put it in their doc or slide tool if connected.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_performance` (the table), `paid_search_diagnose` (driver sentences), `paid_search_proposals` (actions).
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_report campaign_daily --days 56 --out google.csv
   python3 scripts/run.py ads microsoft_report campaign_daily --days 56 --out microsoft.csv
   python3 scripts/run.py perfos report --facts google.csv --start 2026-10-21 --end 2026-11-17 --driver-kpi cpa --goals goals.json [--crm crm.csv]
   ```
   Combine the two CSVs into one facts file (same columns). `goals.json`: `{"nonbrand": {"cpa": 250, "conversions": 60}, "total": {"cost": 15000}}`.
3. **Your own data**: a daily campaign sheet and a CRM export (lead, campaign, stage dates, pipeline value).
