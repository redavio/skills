---
name: audit
description: Audit a Google Ads or Microsoft Ads account (inherited, new client or quarterly) against a B2B paid search checklist - performance vs goals first, then setup health scored 2/1/0 per item with measurement counting double (measurement, settings, structure, targeting, creative, landing pages, bids and budgets, delivery, PMax, AI Max, Microsoft parity), then performance health (impression share, wasted spend, Quality Score, experiments, change discipline, pacing, ads, tracking), and findings ranked by impact on goals. Use when someone asks for an account audit, review, health check or second opinion.
license: MIT
compatibility: Any Agent Skills client. Scoring needs Python 3.10+; reading the account yourself needs google-ads / bingads and your own access.
metadata:
  role: paid-search-manager
  stage: review
  summary: Performance vs goals, one setup health score, ranked findings each tied to its fix.
  needs: Read access to the account (or exports); goals and targets; 90 days of performance; the conversion setup
---

# Audit

Performance vs goals is the name of the game. Best practices explain why performance is off; goals decide
what to fix first. A best-practice miss that isn't hurting results is low priority, not forced.

## Needs
Read-only access or exports: settings, structure, keywords, negatives, ads, assets, audiences,
conversions, bid strategies, change history, search terms, PMax network and placement data, auction
insights, Quality Score; 90 days of performance; goals and targets per segment.

## If something is missing
No goals? Ask for them first (the headline depends on them); if none exist, audit setup only and say so.
Missing a data area: score it "not checked", never pass.

## Method
1. **Snapshot** the account (structure + 90 days) as the before-change record.
2. **Headline**: performance vs goals: pipeline or conversions, CPA or ROAS, budget pacing; brand and non-brand separate lines; on track / behind / ahead. Google's optimization score is an input only.
3. **Part A setup, in build order**, each pass / partial / fail with evidence:
   A0 intake signed off (goals, targets, values, voice of customer, positioning) · A1 measurement (one primary everywhere, stages back by click ID with values, enhanced conversions, no dead or duplicate conversions) · A2 settings (Search only, presence, auto-apply off, auto assets reviewed, verified) · A3 structure (Brand / Non-brand / Competitor, tight themes, geo and language by campaign) · A4 targeting (all match types, fencing between types and ad groups, phrase negatives with no broad, login/support handled, customers excluded, observation audiences) · A5 creative (1 RSA per ad group, 15/4, name in 1-2 headlines, no needless pins, extensions maxed) · A6 landing pages (match, one per theme, CTA to the primary conversion, fast, click IDs survive) · A7 bids and budgets (smart bidding on the right ladder, portfolio per type, Brand ~90% impression share) · A8 delivery (no dead adjustments; dead zones only with data) · A9 PMax (brand excluded, fenced, mirrors Search, own video, URL exclusions, same primary) · A10 AI Max (paused copies, tested as experiments in order, exclusions) · A11 Microsoft parity.
   **Measurement first: if A1 fails, flag that every Part B number is suspect.**
4. **Part B on 90 days vs targets**: B1 impression share (capped winners, capped losers, lost to rank) · B2 wasted spend past the volume gate on every lever · B3 impression-weighted Quality Score, components separately · B4 experiments running, ranked idea bank · B5 change discipline (pace, outside changes, graded) · B6 pacing · B7 disapprovals, ad strength, low assets · B8 tracking health.
5. **Setup health**: 2 / 1 / 0 per item, A1 counts double, as a % of the max. Items for channels not in use (PMax, AI Max, Microsoft) don't count.
6. **Findings**: every fail is a finding, ranked by impact on goals then effort, each mapped to the skill that fixes it (tracking-plan, campaign-structure, negatives-and-fencing, ad-copy, pmax-and-ai-max, budget-rebalance ...). Non-setup findings become initiatives (expansion, optimization, a test). Destructive fixes follow change-safety.
7. **PMax and AI Max get the deepest review**: network mix, lead quality by channel, search themes, brand leakage, AI Max query drift and chosen landing pages.

## Output
1. Headline: performance vs goals table. 2. Setup health %, with the item table (code, status, evidence).
3. Part B table. 4. Ranked findings: what, why it matters for goals, fix, effort. 5. Fix plan for client sign-off.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_audit` runs the checklist with evidence; `paid_search_snapshot`, `paid_search_performance`, `paid_search_search_terms`, `paid_search_parity` for detail.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_snapshot --out snapshot.json
   python3 scripts/run.py ads google_report keywords --days 90 --out kw.csv          # Quality Score
   python3 scripts/run.py ads google_report search_terms --days 90 --out terms.csv
   python3 scripts/run.py ads google_report change_history --days 28
   python3 scripts/run.py perfos audit-score --input audit.json   # {"items": {"A1": "partial", ...}, "channels_on": ["pmax", "microsoft"], "findings": [{"title": "...", "impact": 5, "effort": 2}]}
   ```
3. **Your own data**: Editor exports, UI screenshots and reports; score by hand with the same 2/1/0 rule.
