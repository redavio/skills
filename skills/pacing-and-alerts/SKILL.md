---
name: pacing-and-alerts
description: Daily paid search health check for Google Ads and Microsoft Ads - spend pacing against the monthly budget, volume goals paced to the day (conversions, conversion value, pipeline), CPA or ROAS vs goal, and alerts for missing data, tracking breaks, failed offline imports, disapprovals, parity drift and flagrant spend. Use for a morning check, when asking if campaigns are on pace, overspending or underspending, or whether tracking broke.
license: MIT
compatibility: Any Agent Skills client. Checks need Python 3.10+, standard library only.
metadata:
  role: paid-search-manager
  stage: run
  summary: Pacing vs budget and paced goals, plus alerts that say what broke, where, how bad and the fix.
  needs: Month-to-date spend and results by campaign type; monthly budget; goals; daily clicks and conversions for the last ~3 weeks
---

# Pacing and alerts

Daily is for looking, not acting. Act only on breaks and flagrant spend; everything else waits for the volume gate.

## Needs
Month-to-date spend and results per segment (brand, non-brand, PMax; Google and Microsoft), the monthly
budget and goals, the last ~17 days of daily clicks and conversions, when data last landed.

## If something is missing
Ask for the monthly budget and the goal for each segment. No goal for a segment: report its numbers without a status.

## Method
1. **Spend pacing**: month-to-date spend vs a straight-line pace through yesterday; off by more than the tolerance (default 15%) = over / under. Too early to call before day 3.
2. **Goal pacing**: volume goals (conversions, conversion value, pipeline) paced by the share of the period elapsed; rate goals (CPA, ROAS) compared directly, not paced. On track within 10%; ahead / behind beyond. Brand and non-brand separately; never judge in aggregate.
3. **Alerts** (each says what broke, where, how bad, suggested fix; alerts never change the account):
   - Data missing: no fresh data for 36+ hours.
   - Tracking break: 3 days with 20+ clicks and zero conversions after 14 days that had 2+.
   - Offline import failed; CRM vs platform mismatch beyond tolerance (cohort basis, by click date); match rate drop.
   - Disapprovals or limited ads.
   - Google vs Microsoft parity drift (parity-check).
   - Flagrant spend: an item spent 2x the target CPA with zero conversions (ROAS goal: 2x value per conversion / target ROAS). Review now, even mid-week.
4. **First week after launch**: watch only; learning lasts up to 7 days.

## Output
Top line: on pace / off pace and the one thing to look at. Then a pacing table (segment, platform, spend
vs pace, results vs paced goal, status) and open alerts (severity, what, where, fix, owner).

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_performance` (month to date), `paid_search_diagnose` for anything behind, `paid_search_volume_gate` for flagrant spend, `paid_search_parity` for drift.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_report campaign_daily --days 21 --out daily.csv
   python3 scripts/run.py perfos pacing --spend 8200 --budget 15000 --actual 31 --goal 60
   python3 scripts/run.py perfos tracking --csv daily.csv
   ```
3. **Your own data**: a sheet of daily spend, clicks and conversions per campaign plus the budget and goals.
