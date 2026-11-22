---
name: tracking-plan
description: Plan and check conversion tracking for Google Ads and Microsoft Ads lead generation - one primary conversion bid on everywhere, every funnel stage sent back by click ID (GCLID, MSCLKID) with its own value, enhanced conversions for leads, offline conversion imports from the CRM, a form-fill fallback, UTMs via final URL suffix, and an end-to-end test. Use when setting up or auditing conversion tracking, offline conversions, CRM integration, conversion values, primary vs secondary conversions, or when numbers can't be trusted.
license: MIT
compatibility: Any Agent Skills client. Snapshot and tracking-break checks need Python 3.10+; reading the account yourself needs google-ads and a developer token.
metadata:
  role: paid-search-manager
  stage: set-up
  cadence: Once at setup
  summary: One primary conversion, every stage back by click ID with a value, a fallback, and a test lead read back on both platforms.
  needs: The conversion points (stage, value, where tracked); the CRM; the measurement tier; account access or a conversions list
---

# Tracking plan

If tracking is wrong, nothing else can be trusted: fix it before judging anything. Bidding learns from
exactly one conversion; everything else is fed in for learning and reporting.

## Needs
- Conversion points in funnel order (lead, MQL, SQL, opportunity, closed won), each with its agreed value.
- The CRM, and whether stages can flow back automatically (Tier 1), by scheduled upload (Tier 2), or not at all (Tier 3).
- The account's current conversion actions (read from the account or a screenshot).

## If something is missing
Ask: "Which one conversion should bidding optimize to?" and "Can your CRM store the GCLID on the lead?".
If values aren't agreed, use ACV x chance of becoming a deal per stage and mark them Estimate.

## Method
1. **Route per conversion point**: automatically (Tier 1), by export (Tier 2), website tag (Tier 3), or not sent. Tier 3 is a normal starting point: a form fill with a tag is enough to launch; push toward click IDs from there.
2. **Capture click IDs**: hidden form fields save GCLID and MSCLKID on the lead in the CRM; UTMs and click IDs survive every redirect.
3. **One conversion action per stage** on Google and Microsoft, Google's standard categories (submit lead form, qualified lead, converted lead), each with its own dollar value, counted one per click, 90-day click lookback for B2B.
4. **Exactly one primary**, the same on every campaign type (Search, PMax, AI Max). All other stages secondary (recorded, ignored by bidding). PLG: signup. Never raw form fills as PMax's goal.
5. **Value tiers** on the bid-on stage (high / mid / low fit) if on the value ladder; deep stages (opportunity, closed won) too slow to bid on but imported for learning, reporting, Journey-Aware Bidding and tier calibration.
6. **Turn on**: auto-tagging, MSCLKID, enhanced conversions for leads (UI only: pick a method, then Save), Microsoft UET and goals built natively (imports never carry tracking; Microsoft Max Conversions needs a goal first, an offline goal works).
7. **The pipe**: Tier 1 daily automatic import; Tier 2 scheduled upload (click ID + stage + value + time), no more than a couple of days' lag.
8. **Fallback (break glass)**: with click IDs primary, keep a form-fill conversion with enhanced conversions as a secondary. If uploads stop: promote the form fill, switch to the volume ladder, log it; switch back when fixed (expect a learning reset both ways).
9. **Clean up**: remove dead or duplicate primaries; UTMs exactly as in `shared/NAMING.md`: the account-level final URL suffix for search and PMax (`utm_campaign={_cmp}`, `campaignid={campaignid}`), a campaign-level suffix on display and video campaigns, UTMs on the target URL for ChatGPT ads.
10. **Test end to end**: a test lead reaches the CRM with its click ID and the conversion shows on both platforms, confirmed by reading the account back.
11. **Health**: alert when conversions drop to near zero while clicks continue (3 days of 20+ clicks and no conversions after 14 days that had 2+), or uploads fail. Match rate (click ID, then UTM) is a health metric.

## Output
A table: conversion point, stage, value, primary/secondary, route, Google action, Microsoft goal, status
(built / missing / wrong). Then the tier, owner and date to reach Tier 1, the gaps in priority order, and
the test result. Proposed account changes are listed, never applied: a conversion action change is a
destructive change (client approval and a revert plan; see change-safety).

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_snapshot` lists conversion actions, primaries and enhanced-conversion settings; `paid_search_audit` scores measurement (A1).
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_snapshot --out snapshot.json      # conversion_actions, conversions_30d, account settings
   python3 scripts/run.py perfos tracking --csv daily.csv              # date, clicks, conversions
   ```
3. **Your own data**: screenshots or an export of the conversion actions page, and a daily clicks/conversions sheet.
