---
name: daily
description: The daily paid search check for Google Ads and Microsoft Ads - runs pacing-and-alerts (spend and goal pacing, tracking breaks, failed imports, disapprovals, parity drift) and flags flagrant spend, in that order, so every alert is resolved or owned. Use for a morning check, "what needs attention today", or a daily paid search routine.
license: MIT
compatibility: Any Agent Skills client. Uses the job skills it calls.
metadata:
  role: paid-search-manager
  stage: cadence
  summary: Every morning: pacing, alerts, hygiene and flagrant spend. Look, don't act.
  needs: Account access or yesterday's data; monthly budget and goals
---

# Daily

Daily is for looking, not acting: act only on breaks and flagrant spend.

## Needs
Account access (Redavio connector or your own API) or yesterday's data; the budget and goals. Missing goals: ask in chat.

## Steps
1. **pacing-and-alerts**: data freshness, tracking, offline imports, CRM vs platform match, match rate, spend pacing, goal pacing (brand and non-brand separately), parity drift.
2. **Hygiene**: disapprovals and limited ads (from the same pull).
3. **Flagrant spend**: items at 2x target CPA with zero conversions (volume-gate flag). Review now, propose a change through change-safety only if it's clearly waste.
4. First week after a launch: watch only.

## Output
"All clear" or the list of alerts, each with severity, fix and owner. Nothing is changed without a yes.

## Getting the data
Same modes as the job skills: (1) Redavio connector at `https://app.redavio.com/mcp` (`paid_search_performance`, `paid_search_volume_gate`, `paid_search_parity`); (2) your own API access (Google Ads and Microsoft Advertising developer tokens plus your own OAuth app credentials for each; mode 1 needs none) with the scripts in pacing-and-alerts; (3) your own data.
