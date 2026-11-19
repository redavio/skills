---
name: build
description: Build Google Ads Search campaigns (and mirror them on Microsoft Ads) from an agreed plan through the API - offline plan check, Google validate-only dry run, then everything created PAUSED in one atomic request and confirmed by reading the account back, followed by a parity check. Use when someone wants to build, rebuild or port paid search campaigns, push a campaign plan to Google Ads, or turn a keyword and ad copy plan into a live (paused) account.
license: MIT
compatibility: Plan check needs Python 3.10+ only. Building needs google-ads, your own Google Ads API access (developer token) and Standard or Admin access on the account; or the Redavio connector.
metadata:
  role: paid-search-manager
  stage: set-up
  cadence: Once at setup
  summary: Plan -> check -> Google dry run -> paused build -> read-back -> parity, with a yes before any write.
  needs: The plan (campaigns, ad groups, keywords, negatives, ads, assets, budgets, bidding); the account; the person's explicit yes before the live build
---

# Build

Builds are paused, verified and approved. Nothing goes live from this skill: launch-check does that.

## Needs
A plan file (format in `references/plan-format.md`), usually assembled from campaign-structure,
keyword-research, negatives-and-fencing, ad-copy and forecast-and-budget. The account ID. The person's yes.

## If something is missing
Ask for whatever the plan lacks (daily budgets, a landing page per ad group, brand terms). Missing
copy? Run the ad-copy skill. Don't build a campaign with placeholder copy.

## Method
1. **Order** (the checklist): measurement first (tracking-plan), then settings, structure, targeting, creative, landing pages, bids and budgets, delivery, PMax, AI Max, Microsoft.
2. **Settings baked in**: Search only (partners and Display off), location = presence, smart bidding only (Maximize Conversions or Maximize Conversion Value, no target on a new campaign), one portfolio per campaign type (test copies separate), all match types, shared negative lists attached, account-level assets, 24/7 all devices with no bid adjustments, AI Max copies built paused with URL exclusions.
3. **Plan check offline**: character and count limits, no broad negatives, no blocked product terms, every ad group has keywords and an ad with a final URL, names follow `channel|type|theme|geo|language`, warnings for targets at launch.
4. **Dry run**: Google validates every operation without saving (validate-only). Fix anything flagged.
5. **Show what will be created** (counts per campaign) and **ask for an explicit yes**.
6. **Build**: one atomic request with temporary IDs (all or nothing). Aborts if a campaign name already exists. Campaigns are PAUSED; ad groups, keywords and ads inside are enabled, so say clearly: switching a campaign on makes everything in it live.
7. **Read back** from the API: status, ad groups, keywords and ads per campaign vs the plan. Never trust the create response. A mismatch = stop and report.
8. **UI-only items** to tick: enhanced conversions for leads, advertiser verification, Data Manager connections, auto-apply recommendations off.
9. **Microsoft**: net-new account = one-time Import from Google is fine, then rebuild tracking natively (UET, MSCLKID, goals) and set own budgets and targets; after that, build Microsoft from the same plan, never scheduled imports. Run the parity-check skill.
10. If a field or resource isn't available in the API version or account: stop and report, don't improvise.

## Output
Plan check result, dry-run result, the counts to be created, then (after the build) the read-back table
per campaign (status, ad groups, keywords, ads: have/want) and the UI-only tick list.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_snapshot` reads the account; `paid_search_proposals` queues a build for approval in Redavio, which builds paused and reads back.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_build plan.json --check      # offline
   python3 scripts/run.py ads google_build plan.json              # Google dry run, saves nothing
   python3 scripts/run.py ads google_build plan.json --live       # ONLY after the person's yes
   ```
   Credentials: `google-ads.yaml` or `GOOGLE_ADS_*` env vars; account via `--customer-id` or `GOOGLE_ADS_CUSTOMER_ID`.
3. **Your own data**: keep the plan in a Google Sheet (one row per keyword / ad) and convert it to the plan JSON; or upload it through Google Ads Editor yourself, paused.
