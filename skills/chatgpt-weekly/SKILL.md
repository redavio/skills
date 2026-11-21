---
name: chatgpt-weekly
description: "Review ChatGPT ads weekly for B2B SaaS: put every ad group through the volume gate against the account's own CPA (or the target), propose which hints or ad groups to cut and which to scale, and check every ad against OpenAI's limits. Use for the weekly ChatGPT ads review, or when someone asks what to change in ChatGPT ads or why its CPA is high."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; pulling data needs your own OpenAI Ads API key.
metadata:
  role: chatgpt-ads-specialist
  stage: run
  cadence: Weekly
  summary: "Each week: which ad groups to cut or scale against your account, and every ad checked against OpenAI's limits."
  needs: "Ad group insights by week (2+ full weeks): ad group, cluster, impressions, clicks, spend, conversions; optional target CPA; your ads"
---

# ChatGPT ads weekly review

Each ad group is judged against the account (or your target), and only cut when it's 95% surely worse. Broad hints are the usual cause of a bad ad group.

## Needs
- Ad group insights by week, 2+ full weeks: week, campaign, ad_group, cluster, impressions, clicks, spend, conversions.
- Optional: target CPA, goal conversion rate, and the current ads (ad, ad_group, title, body, target_url).

## If something is missing
No conversions tracked: review on CTR and CPC only and point to chatgpt-tracking. Fewer than 2 weeks: say so and wait.

## Method
1. **Rule out broken data first**: conversions at zero across every ad group means tracking or lag, not the ad groups.
2. **Run the review** (don't do it by hand):
   ```
   python3 scripts/run.py perfos chatgpt-weekly --csv insights.csv --ads ads.csv [--target-cpa 250]
   ```
3. **Read the verdicts**: **cut** = past the click line and below the account's conversion rate: narrow its hints to what converts in search, or pause it. **flag** = spend at 2x CPA with no conversions, still below the line: watch. **scale** = beating the account: propose more budget or a higher bid. **watch** = not enough data.
4. **Ads**: fix anything the check lists; replace the lowest-CTR ad per ad group once it has 1,000+ impressions.
5. **Pacing**: spend vs the daily budget; under-delivery usually means hints too narrow or a bid too low.

## Output
A table sorted cut, flag, scale, watch: ad group, cluster, clicks, conversions, spend, CPA, CPA vs account, verdict, proposed change. Then ad problems, dates used and the benchmark used. **Proposals only**: a person makes each change in Ads Manager.

## Getting the data
1. **Your own API key** (read only; Ads Manager > Settings > General > API Keys, one per ad account): `export OPENAI_ADS_API_KEY=...` then
   ```
   python3 scripts/run.py ads chatgpt_report insights --days 28 --clusters clusters.json --out insights.csv
   ```
2. **Your own data**: an Ads Manager ad group export with the same columns, or pasted in chat.
