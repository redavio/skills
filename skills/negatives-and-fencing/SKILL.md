---
name: negatives-and-fencing
description: Build and check negative keywords for Google Ads and Microsoft Ads - shared lists for brand terms, competitor names and junk, fencing between Brand, Non-brand, Competitor and PMax, exact-match fencing between ad groups so each search lands in the ad group built for it, login and support negatives, plurals, and checks for broad negatives or negatives that block real product terms. Use when setting up negatives, fixing keyword cannibalization, brand leaking into non-brand or PMax, or auditing a negative keyword list.
license: MIT
compatibility: Any Agent Skills client. Fencing helper needs Python 3.10+, standard library only.
metadata:
  role: paid-search-manager
  stage: set-up
  summary: Shared negative lists, campaign and ad-group fencing, login/support negatives, no broad negatives.
  needs: Brand terms; competitors (and which names are common words); campaigns with their ad groups' keywords; product terms that must never be negated
---

# Negatives and fencing

## Needs
Brand terms and misspellings, competitor names (flag common-word names), each campaign's ad groups with
their keywords, product terms to protect, and whether the product has a free plan.

## If something is missing
Ask for brand misspellings and whether "free" is something they offer. Never negate a term you're unsure is junk: list it as "check".

## Method
1. **Shared lists, built once, attached across campaigns** (`negatives|brand_terms`, `negatives|competitors`, `negatives|junk`):
   - Brand terms -> negative in Non-brand and Competitor; PMax uses a brand exclusion (phrase negatives if Google doesn't recognise the brand yet).
   - Competitor names -> negative in Brand and Non-brand.
   - Junk (jobs, careers, salary, hiring, course, tutorial, template, free if not offered) -> everywhere.
2. **Match rules**: phrase by default; **never broad**; exact only to isolate a head term (keep the head query in its own campaign, keep the long tail). Add plurals: negatives don't match close variants. Never negate a real product term, or "free" if the product is free.
3. **Ad-group fencing**: inside a campaign, each ad group carries the other ad groups' keywords as exact negatives, so "agency crm pricing" lands in the pricing ad group, not wherever it auctions best.
4. **Login and support**: own brand + login / sign in / support / cancel as phrase negatives. Competitor login/support negative by default; opt in to a low-bid test only on a churn signal.
5. **Common-word competitor names**: keywords phrase and exact only; their negatives phrase.
6. **AI Max and PMax**: same lists plus URL exclusions (careers, blog, support, login, legal).
7. **Ongoing**: daily threshold check and weekly search term review (search-term-review skill); new negatives come from data through the volume gate.

## Output
The three shared lists with where each attaches, the login/support list, the ad-group fencing per
campaign, and problems found (broad negatives, blocked product terms, missing fences). Proposals only;
adding negatives is a routine change the person approves (change-safety).

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_snapshot` lists keywords, negatives and shared lists; `paid_search_search_terms` shows leaks.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_entities --out google.json        # current keywords and negatives
   python3 scripts/run.py perfos fence --input fence.json
   ```
   `fence.json`: `{"brand_terms": ["example co"], "competitors": [{"name": "Rival", "common_word": false}], "campaigns": {"search|nonbrand|crm|us|en": {"pricing": ["crm pricing"], "demo": ["crm demo"]}}, "protected_terms": ["crm pricing"], "offered_free": false}`.
   Apply one approved negative: `python3 scripts/run.py ads google_apply negative --campaign C --text "jobs"` (dry run; `--live` only after a yes).
3. **Your own data**: an Editor export of keywords and negatives, or a sheet.
