---
name: ad-copy
description: Write and check responsive search ads and assets for Google Ads and Microsoft Ads from voice of customer and the messaging guide - one RSA per ad group with 15 headlines and 4 descriptions, the right headline mix, competitor ad rules, sitelinks, callouts, structured snippets, and character limits checked before anything is built. Use when someone asks for ad copy, RSA headlines and descriptions, extensions, competitor ads, or to review ads for limits and best practice.
license: MIT
compatibility: Any Agent Skills client. Limits check needs Python 3.10+, standard library only.
metadata:
  role: paid-search-manager
  stage: set-up
  summary: RSAs and assets written from the customer's own words, 15 headlines and 4 descriptions, limits checked.
  needs: Ad group themes and landing pages; voice of customer quotes; differentiators and proof; approved copy and words to avoid
---

# Ad copy

## Needs
Each ad group's theme and landing page; voice-of-customer quotes; pillars, differentiators and proof;
the approved copy bank; words, claims and trademarks to avoid.

## If something is missing
Ask for 3-5 real customer quotes and one proof point (a number, a logo, a rating). Without them, draft
from the site and mark every line "needs approval". New claims, numbers or competitor statements always need the client's sign-off.

## Method
1. **Source**: the customer's own words and the copy bank. Lines assembled or lightly adapted from the bank need no approval.
2. **One RSA per ad group**: 15 headlines (30 characters) and 4 descriptions (90), both paths (15 each). No pins unless legal or brand requires them.
3. **Headline mix**: 8-10 tied to the ad group's theme; about 5 shared (offer, proof, risk reversal); 1-2 with the company or product name in every ad group (Brand, Non-brand and Competitor). No duplicates.
4. **Descriptions**: one job each (what it does, proof, offer, call to action).
5. **Competitor ads**: a few "X alternative" / "vs X" headlines, the rest true differences. Swap to generic wording on trademark disapproval. Microsoft editorial is stricter on trademarks.
6. **Assets maxed at account level**: sitelinks (text 25, descriptions 35), callouts (25), structured snippets (an allowed header, 3+ values of 25), images, business name and logo (need advertiser verification), lead form. Campaign level only where a theme needs its own.
7. **Ad strength** good or better, but never at the cost of relevance. Tag headlines by type (offer, proof, differentiator, competitor, name) so tests can learn which types win.
8. **AI Max text guidelines**: words and claims to avoid from the copy bank.

## Output
Per ad group: headlines (with character counts and type tag), descriptions, paths, final URL; then the
assets. Then the limits check result and lines needing client approval.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_snapshot` returns current ads, strength and approval status.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens): `python3 scripts/run.py ads google_snapshot --out snapshot.json` (current ads); check new copy with
   ```
   python3 scripts/run.py perfos copy-check --input copy.json
   ```
   `copy.json`: `{"rsas": [{"ad_group": "pricing", "headlines": [...15], "descriptions": [...4], "path1": "pricing"}], "sitelinks": [["Pricing", "Plans for every team", "Start free"]], "callouts": ["Free Trial"], "snippet_header": "Types", "snippet_values": ["A", "B", "C"]}`.
3. **Your own data**: customer quotes, reviews and the positioning doc pasted in chat or in a doc.
