---
name: linkedin-weekly
description: "Review LinkedIn Ads weekly for B2B SaaS: awareness ad sets judged on cost to reach (CPM), impressions per member per week and creative fatigue (CTR falling); the engaged campaign's ad sets through the volume gate on conversions. Proposes which to refresh, lower, cut or scale. Use for the weekly LinkedIn review, or when someone asks what to change in LinkedIn or why it's expensive."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; reading LinkedIn needs the Redavio connector or a Campaign Manager export.
metadata:
  role: linkedin-ads-manager
  stage: run
  cadence: Weekly
  summary: "Each week: which LinkedIn ad sets to refresh, lower, cut or scale, judged the way each campaign should be."
  needs: "Weekly performance per ad set (2+ full weeks) and each campaign's audience size"
---

# LinkedIn weekly review

Awareness and conversion are judged differently: awareness on what it costs to reach the audience and whether the creative is wearing out; the engaged campaign on conversions, only once there's enough data.

## Needs
- Weekly rows per ad set (2+ full weeks): week, campaign, ad_set, format, impressions, clicks, spend, conversions.
- Each campaign's audience size (for frequency). Optional: target CPA.

## If something is missing
No rows: nothing has run yet; come back after 2 full weeks live. No conversions anywhere: tracking first (linkedin-tracking).

## Method
1. **Pull the weeks**: `paid_linkedin_report` (rows and audience sizes in one call).
2. **Run the review** (don't do it by hand):
   ```
   python3 scripts/run.py perfos linkedin-weekly --input report.json [--target-cpa 400]
   ```
3. **Read the verdicts**: **refresh** = CTR fell 30%+ from its first weeks: new creative. **flag** = over 3 impressions per member a week (lower the budget) or CPM 1.5x the account's (check targeting overlap). **cut** / **scale** = the engaged campaign through the volume gate against its own CPA. **keep** / **watch** = in line, or under 5,000 impressions.
4. **Never judge awareness on LinkedIn's conversions**: its 7-day click attribution is shown, not used; pipeline is linkedin-measure's job.

## Output
A table sorted cut, refresh, flag, scale, keep, watch: ad set, format, impressions, CPM, CTR, impressions per member, verdict, reason, proposed change. **Proposals only**: a person approves each change.

## Getting the data
1. **Through the Redavio connector** (app.redavio.com/mcp, LinkedIn connected): `paid_linkedin_report` returns weekly rows per ad set and each campaign's audience size.
2. **Your own data**: a Campaign Manager export with the same columns, or numbers pasted in chat. Nothing in this skill writes to LinkedIn.
