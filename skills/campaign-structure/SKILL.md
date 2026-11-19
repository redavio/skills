---
name: campaign-structure
description: Design the account structure for Google Ads and Microsoft Ads Search - Brand, Non-brand and Competitor campaigns, one ad group per theme, geo and language split by campaign, paused AI Max copies, PMax mirroring Search themes, one bid portfolio per campaign type, and a warehouse-friendly naming convention (channel|type|theme|geo|language). Use when planning a new paid search account, restructuring one, naming campaigns, or deciding how many campaigns and ad groups to have.
license: MIT
compatibility: Any Agent Skills client. Name helper needs Python 3.10+.
metadata:
  role: paid-search-manager
  stage: set-up
  cadence: Once at setup
  summary: Brand / Non-brand / Competitor, one ad group per theme, portfolios per type, names that split cleanly in SQL.
  needs: Offerings, brand terms, competitors; locations and languages; anything with its own budget, target or goal
---

# Campaign structure

## Needs
Offerings (each becomes a Non-brand ad group), brand terms, competitors, locations and languages, and
anything that needs its own budget, target, geo or goal.

## If something is missing
Ask: "Does any product or market need its own budget or goal?" Default to the standard three campaigns
per geo/language until something says otherwise.

## Method
1. **Campaigns**: always Brand / Non-brand / Competitor, separate. Split into more only when budget, target, geo, language or goal differ (never by device or platform when volume is low).
2. **Ad groups**: one per theme, regardless of volume (smart bidding learns at campaign and portfolio level).
   - Brand: pure brand / brand + product / brand + pricing or signup.
   - Non-brand: one per offering (product, feature, solution, job to be done).
   - Competitor: one per competitor.
3. **Geo and language** split by campaign, never ad group; identical on Google and Microsoft (Microsoft allows ad group geo; don't use it). Location option = presence. Google matches ads on the language they're written in: one language per campaign.
4. **Shells**: AI Max copies of Non-brand, Brand and Competitor built and left paused (tested later as experiments). PMax: asset groups mirror the Non-brand themes; a new PMax campaign only when budget, target, geo or goal differ.
5. **Portfolios**: one bid portfolio per campaign type (Brand, Non-brand, Competitor); test copies (AI Max) get their own so tests aren't pooled. Volume matters at portfolio level.
6. **Fencing** between campaign types and between ad groups (negatives-and-fencing skill).
7. **Naming**: `channel|type|theme|geo|language`, lowercase snake_case values, "|" never inside a value. Examples: `search|brand|core|us|en`, `search|nonbrand|agency_crm|us|en`, `search|nonbrand|agency_crm_aimax|us|en`, `pmax|nonbrand|agency_crm|us|en`. Portfolios `portfolio|nonbrand`, shared lists `negatives|brand_terms`. Join on IDs, never names, so renames never break history.
8. **Hero campaigns** (graduating winners to exact) are an optimization move later, not a structure rule: every split thins smart-bidding data.

## Output
A tree: campaign (name, type, geo, language, portfolio, daily budget if known) > ad group (theme, landing
page) > keyword themes, plus the paused shells and PMax asset groups. Flag anything that breaks a rule.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_snapshot` shows the current structure to restructure from.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens): `python3 scripts/run.py ads google_entities --out google.json` for the current tree; build names with `python3 scripts/run.py perfos name --channel search --type nonbrand --theme "Agency CRM" --geo us --language en`.
3. **Your own data**: an Editor export or a sheet of campaigns and ad groups.
