---
name: keyword-research
description: Build the keyword list for Google Ads and Microsoft Ads Search campaigns from the business itself (offerings, brand terms, competitors), with Keyword Planner volume and CPC shown as context only, sorted into Brand, Non-brand and Competitor with match types. Use when someone asks for keyword research, which keywords to bid on, keyword ideas, search volume, or how to structure keywords for a new paid search account or a new offering.
license: MIT
compatibility: Any Agent Skills client. Keyword Planner pulls need Python 3.10+, google-ads and your own API access (developer token); otherwise uses Redavio or exported data.
metadata:
  role: paid-search-manager
  stage: set-up
  cadence: Once at setup
  summary: Keywords chosen on sense from the offerings, brand and competitors; volume and CPC are context, never the decider.
  needs: Offerings with the words customers use; brand terms; competitors; target locations and language
---

# Keyword research

If a keyword makes sense for the business, it gets bid on. Search volume and bid ranges are pulled
and shown alongside, as context only: they never add, cut or rank a keyword. Low volume is fine:
smart bidding learns at campaign and portfolio level, so thin ad groups are fine.

## Needs
- Offerings (products, features, jobs to be done) and the words customers use for each.
- Brand terms and misspellings; competitors (and whether each name is a common word).
- Locations and language.

## If something is missing
Ask: "What do customers type when they need this?" or "Which competitors do you lose deals to?".
If they have no list, propose seeds from their site and ask them to confirm each. Never add a
keyword the business can't serve.

## Method
1. **Seeds from the business**, not a tool: one seed set per offering, the brand set, one set per competitor.
2. **Pull volume and CPC** (Keyword Planner on Google; Microsoft's Ad Insight where available) for each seed set. Keep ideas that contain the seed phrase; read every other idea and keep only what makes sense. Watch for ambiguous seeds pulling junk (a product called "shape" pulls "draw shapes"). New brands often show 0: that's normal.
3. **Sort into campaign types:**
   - **Brand**: pure brand / brand + product / brand + pricing or signup (three ad groups).
   - **Non-brand**: one ad group per offering, regardless of volume.
   - **Competitor**: one ad group per competitor.
4. **Match types**: exact, phrase and broad on every keyword unless there's a stated reason. Competitor names that are common words (e.g. a tool named after a dictionary word): phrase and exact only. Competitor broad only on "X alternative" / "X pricing" style terms, never the bare name (it drifts into their login and support).
5. **Parity**: any keyword that names Google gets a Microsoft/Bing twin, and the same list runs on both platforms.
6. **Junk and fencing seeds**: note obvious negatives you saw (jobs, careers, salary, free if not offered, tutorials) for the negatives-and-fencing skill.
7. Volume becomes the forecast input (forecast-and-budget). It never decides.

## Output
A table per campaign type: ad group, keyword, match types, Google monthly searches, Microsoft monthly
searches, low-high CPC, and a "context only" note at the top. Then the junk terms seen. Save as CSV
(`keyword, campaign_type, platform, monthly_searches, low_cpc, high_cpc`) so the forecast can read it.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_forecast` returns keyword volume and CPC with the forecast; `paid_search_accounts` picks the account.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_keyword_ideas --type nonbrand --seed "agency crm" --seed "crm for agencies" --only-containing-seed --out ideas.csv
   python3 scripts/run.py ads google_keyword_ideas --type brand --seed "your brand" --append --out ideas.csv
   ```
   `--geo 2840` (United States) and `--language 1000` (English) are Google's constant IDs; change them for other markets.
3. **Your own data**: an export from Keyword Planner, Microsoft Ads Keyword Planner or any SEO tool, in a sheet with the same columns.
