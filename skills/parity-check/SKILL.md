---
name: parity-check
description: Compare Google Ads and Microsoft Ads Search accounts for drift - campaigns, ad groups, keywords, match types, negatives, ads and status that exist on one side and not the other or differ - plus Microsoft-specific setup (native UET tracking, MSCLKID, conversion goals, no scheduled Google imports, own budgets and targets). Use after a build or big change, weekly, or when someone asks whether Bing / Microsoft Ads matches Google Ads.
license: MIT
compatibility: Any Agent Skills client. Comparison needs Python 3.10+; exporting yourself needs google-ads and bingads with your own access.
metadata:
  role: paid-search-manager
  stage: run
  summary: Google vs Microsoft drift flagged entity by entity; budgets and targets deliberately not compared.
  needs: Structure from both accounts (or exports); which differences are intentional
---

# Parity check

Default is parity: Microsoft mirrors Google unless there's a stated reason. The check flags drift;
it never fixes it.

## Needs
Both accounts' Search structure (campaigns, ad groups, keywords with match types, negatives, ads, status)
and any intentional differences.

## If something is missing
Only one platform connected? Say parity can't be checked and list what's needed. Ask which differences are deliberate before calling them drift.

## Method
1. **Compare** by (type, campaign, ad group, name): missing on Microsoft, missing on Google, or mismatched status, match type, geo, language, ad text. Names must match; join on names here because IDs differ across platforms.
2. **Not compared**: budgets and targets. Microsoft has its own, judged on its own cost per qualified lead; start at 10-15% of search budget, scale on performance.
3. **Microsoft setup checks**: UET tag, MSCLKID and conversion goals built natively (imports never carry tracking); no scheduled Google imports running (they work until they don't); language setting matches the ads; owned-and-operated sites only (no syndication); same geo split by campaign (don't use ad group geo).
4. **Expected Microsoft-only extras** (not drift): LinkedIn profile targeting (observation -> bid adjustment -> target-only for ABM), Microsoft in-market lists, extra bid adjustments.
5. **Watch disapprovals**: Microsoft editorial is stricter on trademarks.
6. Cadence: after every build or big change, and weekly.

## Output
Top line: clean, or N drift items. Then a table: issue, type, campaign, entity, field, Google, Microsoft,
suggested fix. Then the Microsoft setup checks pass/fail. Fixes are proposals for change-safety.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and Microsoft. `paid_search_parity` runs the comparison.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_entities --out google.json
   python3 scripts/run.py ads microsoft_entities --out microsoft.json
   python3 scripts/run.py perfos parity --google google.json --microsoft microsoft.json
   ```
3. **Your own data**: Google Ads Editor and Microsoft Ads Editor exports converted to lists of `{type, campaign, ad_group, name, status, match_type}`.
