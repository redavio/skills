---
name: search-term-review
description: Review a Google Ads or Microsoft Ads search terms report and propose negatives and new keywords using a click-based volume gate, judged against the account's own goal (CPA, ROAS, conversions or conversion value). Covers standard Search, AI Max and Performance Max search terms. Use when someone shares search query data, asks about wasted spend, negative keywords, irrelevant queries, or which search terms to add as keywords.
license: MIT
compatibility: Any Agent Skills client (Claude.ai, Claude Code, others). Scripts need Python 3.10+, standard library only; pulling data yourself needs google-ads or bingads and your own API access.
metadata:
  role: paid-search-manager
  stage: run
  summary: Cut or promote search terms against goal, with the volume gate deciding when there's enough data.
  needs: Search terms with clicks, conversions and cost (whole weeks, 7+ days); goal conversion rate per segment; target CPA or target ROAS per segment (or a conversions or value goal)
---

# Search term review

Every search term is judged against the campaign's goal, never gut feel. A term is cut or
promoted only when it has enough clicks to call; below that the honest answer is "watch".
Brand and non-brand (competitor sits with non-brand) always use their own goals.

## Needs
- Search terms: term, campaign, clicks, conversions, cost (plus conversion value for value goals). Whole weeks, at least 7 days; 28 is typical.
- Per segment (brand, non-brand, PMax): the goal conversion rate, and the goal it bids to: target CPA, target ROAS, or a conversions / conversion value goal with no target.
- Optional: the terms already added as keywords or negatives, and product terms that must never be negated.

## If something is missing
Ask in chat instead of stopping, one short question at a time: "What conversion rate do you
consider on goal for non-brand?" or "What's the target CPA for brand?". If they don't know the goal
conversion rate, offer to use their own last 90 days for that segment and say so in the output. Never
invent a goal. If a segment has no goal, list its terms as "no goal set" and skip the verdicts.

## Method
1. **Rule out broken data first.** If conversions dropped to zero across the board, or the window
   ends inside the conversion lag (B2B often 7-30 days), say so and stop cutting: it's tracking or lag, not the terms.
2. **Segment.** Brand / non-brand / competitor / PMax, from campaign names (`channel|type|theme|geo|language`) or ask. Never pool brand with non-brand.
3. **Volume gate per term** (run the math, don't do it by hand):
   - **Cut** when clicks pass the line and the term is still below goal: 0 conversions: 3 / goal CVR; 1: 5 / goal CVR; 2: 7 / goal CVR; 3: 9 / goal CVR (95% sure it's worse than goal). At a 5% goal: 60, 100, 140, 180 clicks.
   - **Promote** at 3+ conversions with conversion rate at or above goal and beating the target (CPA at or under target, or ROAS at or over target).
   - **Flag (view only)**: spend at 2x the target CPA with zero conversions, even mid-week. For a ROAS goal, the target CPA is value per conversion / target ROAS.
   - Everything else: **watch**. If the line isn't reached, extend the window a week at a time.
4. **Pool thin terms** by shared word or theme ("free", "jobs", "template") within the same campaign type only, and run the gate on the pool. A pool verdict becomes one phrase negative.
5. **Turn verdicts into changes:**
   - Cut: a negative. **Phrase match by default; exact only to isolate a head term; never broad.** Add the plural too (negatives don't match close variants). Never negate a real product term or "free" if the product is free.
   - Promote: add as an exact keyword in the ad group built for it, and as an exact negative in the other ad groups of that campaign so it lands there.
   - Brand terms showing in non-brand or PMax: a fencing gap. Add brand as a phrase negative (PMax: brand exclusion). Login, support and "cancel" queries: phrase negatives.
   - Competitor login/support queries: negative by default.
6. **AI Max and PMax terms**: same gate. AI Max: also check the landing page it chose; prune with negatives and URL exclusions (careers, blog, support, login, legal). PMax: Google only shows search term insights by category; cut at category level with campaign negatives.

## Output
A table sorted cut, promote, flag, then watch count only:

| Term | Campaign | Clicks | Conv | Cost | Verdict | Change proposed | Why |
|---|---|---|---|---|---|---|---|

Then: dates used, goals used (and which were their own 90-day numbers), anything ruled out (tracking, lag),
and the count of terms on watch. **Proposals only.** Nothing is applied without the person's yes for
each change; see the change-safety skill for how a change is applied and read back.

## Getting the data
Use the first that works:
1. **Redavio connector** (Claude or any MCP client): add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. Use `paid_search_accounts` to pick the account, `paid_search_search_terms` for the report, `paid_search_volume_gate` for the verdicts.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_report search_terms --days 28 --daily --out terms.csv
   python3 scripts/run.py ads microsoft_report search_terms --days 28 --daily --out terms_ms.csv
   python3 scripts/run.py perfos terms --csv terms.csv --goals goals.json
   ```
   `goals.json`: `{"nonbrand": {"cvr": 0.04, "cpa": 250}, "brand": {"cvr": 0.15, "cpa": 40}}` or for ROAS `{"nonbrand": {"cvr": 0.03, "roas": 4, "value_per_conversion": 900}}`. With a `date` column, windows are whole weeks automatically.
3. **Your own data**: an exported CSV or a Google Sheet with columns `term, campaign, segment, clicks, conversions, cost` (optional `date`, `conversion_value`). Point `run.py perfos terms --csv` at it, or paste it in chat and the same rules apply.
