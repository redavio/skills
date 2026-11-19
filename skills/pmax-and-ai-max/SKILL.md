---
name: pmax-and-ai-max
description: Set up and review Google and Microsoft Performance Max and AI Max for Search on a lead-gen account - asset groups by theme, search themes, audience signals, brand exclusions, URL exclusions, placement exclusions, the channel and search terms reports, AI Max as a 50/50 experiment against standard Search, and observation audiences from the ICP. Use when launching or auditing PMax or AI Max, when PMax brings junk leads or eats brand traffic, or when deciding whether to turn AI Max on.
license: MIT
compatibility: Any Agent Skills client. Reports and math need Python 3.10+; pulling data yourself needs google-ads and a developer token.
metadata:
  role: paid-search-manager
  stage: set-up
  cadence: Once at setup, then weekly
  summary: PMax and AI Max set up fenced and measured on the real goal; AI Max proven by experiment, never switched on blind.
  needs: Search themes and their top keywords; the primary conversion; brand terms; ICP (industries, sizes, roles); customer lists or site visitor audiences; for reviews, 4+ weeks of data
---

# PMax and AI Max

## Needs
Search ad groups and their top keywords (themes), the one primary conversion, brand terms, assets per
theme (headlines, long headlines, descriptions, images, logo, video), audiences (customer lists, site
visitors, in-market), the ICP for observation audiences. For a review: 4+ weeks of channel, search
term and landing page data, plus lead quality by source if the CRM has it.

## If something is missing
Ask for the primary conversion first; PMax must never bid on raw form fills. No video? Say Google will
auto-generate one (it can't be turned off by API) and recommend uploading their own.

## Method: Performance Max
1. **Launch with Search on day one**, bidding on the same primary conversion as Search, as a test with a read date. Same ladder: no target first, then the goal.
2. **Structure**: new PMax campaign only when budget, target, geo or goal differ; otherwise asset groups by solution theme mirroring Search ad groups. Personas go in audience signals, not asset groups. Don't over-split at low volume.
3. **Fencing**: own brand excluded via brand exclusions (so Brand Search keeps brand traffic); shared competitor and junk negatives at campaign level.
4. **Search themes** per asset group = that theme's top Search keywords. **Audience signals**: customer lists, site visitors, in-market, custom segments (competitor terms and URLs). Exclude customers, employees, recent converters. Signals are hints, not targeting.
5. **Assets**: full set per asset group (headlines 30, long headlines 90, descriptions 90 with one of 60 or fewer, landscape, square and portrait images, logos, own video), one landing page per theme. Business name and logo via brand guidelines.
6. **URL expansion** on with exclusions: careers, blog, support, login, legal.
7. **Brand safety**: account-level placement exclusions (sites, apps, YouTube; one list shared across PMax, Display, Demand Gen), junk app categories, standard content suitability. Turn on the Display / Search Partners opt-out when it reaches the account.
8. **Microsoft PMax**: images 1.91:1 and 1:1; LinkedIn signals don't show in API reads, confirm in the UI.
9. **Weekly review**: network split (Search vs Display / YouTube) and lead quality by channel; search term insights; placements. Pause or exclude what doesn't produce qualified stages (volume gate). Need hard channel control? Use Demand Gen instead.

## Method: AI Max for Search
1. What it is: one switch on a Search campaign adding search term matching, text customization, and final URL expansion (needs text customization).
2. **Build paused copies** of Non-brand, Brand and Competitor (`..._aimax` theme, own portfolio). Paused shells cost nothing.
3. **Test, never switch on blind**: a 50/50 campaign experiment on the live base (needs an enabled base campaign). Order: Non-brand, then Brand, then Competitor (riskiest: drifts into competitor login/support). Never two live copies competing.
4. **Win** = qualified stage or value at 95% confidence (test-read skill), then apply to the base.
5. **Settings**: all three features on; URL exclusions as above; URL expansion off if the client needs fixed pages or pinning is legally required (it ignores pins). Text guidelines from the words to avoid. Brand fenced (phrase negatives if the brand isn't in Google's brand list).
6. **Weekly**: AI Max search terms and the landing pages it picked; prune with negatives and URL exclusions; judge on qualified stage or value, not clicks.
7. Microsoft has AI Max too (same three features).

## Method: observation audiences (Search)
At ad group level, observation only (never targeting) at launch: in-market and affinity (Google refuses life events and detailed demographics on Search), custom segments of competitor terms and URLs, site visitors (all, pricing, demo), trial users, CRM stages (MQL, SQL, open opp, closed lost); Microsoft adds LinkedIn company, industry, job function and seniority from the ICP (observe, then bid adjustment, then target-only for ABM). First-party data only; no purchased contact lists as ad audiences.

## Output
Setup: a checklist per campaign with each rule pass / missing. Review: tables for network split, search
term categories, landing pages and placements with volume-gate verdicts, then proposed exclusions and
negatives. Proposals only; the person approves each change.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_snapshot` (settings), `paid_search_search_terms` (incl. AI Max and PMax terms), `paid_search_performance` (network split), `paid_search_test_read` (experiment result), `paid_search_audit` (A9, A10).
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_report pmax_networks --days 28
   python3 scripts/run.py ads google_report pmax_search_terms --campaign-id 1234567890 --days 28
   python3 scripts/run.py ads google_report expanded_landing_pages --days 28
   python3 scripts/run.py ads google_snapshot --out snapshot.json      # ai_max section
   ```
   PMax asset groups and Microsoft PMax are built in the platform UI (or via the Redavio connector) from the plan, paused.
3. **Your own data**: channel performance and search term insights exported from the Google Ads UI.
