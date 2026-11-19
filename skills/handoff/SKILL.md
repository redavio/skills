---
name: handoff
description: Package a Google Ads and Microsoft Ads account for a clean handoff or offboarding - current structure, bidding path, targets and budgets, conversion setup and tracking tier, the change log, open initiatives, running tests with read dates, known risks, and access to hand over. Use when an engagement ends, an account changes hands, a new person takes over paid search, or someone asks for account documentation.
license: MIT
compatibility: Any Agent Skills client. Reading the account yourself needs google-ads / bingads and your own access.
metadata:
  role: paid-search-manager
  stage: review
  cadence: When an engagement ends
  summary: Everything the next owner needs: state, settings, tracking, history, open work and access.
  needs: Read access to the accounts (or exports); the change log; the test log; open initiatives
---

# Handoff

## Needs
Read access or exports for both platforms, the change log, the test log, open initiatives, goals and the intake.

## If something is missing
No change log? Export the platform change history (Google keeps 30 days in the API) and say older history is in the UI only.

## Method
1. **Current state**: structure tree (campaigns, ad groups, themes, naming convention), bidding ladder and portfolios, targets and daily budgets per campaign, Brand coverage approach, Microsoft's own budgets and targets.
2. **Measurement**: conversion actions (which is primary, values, routes), tracking tier and owner, offline import schedule, enhanced conversions, UTMs / final URL suffix, known gaps.
3. **Rules in use**: goals per segment, step limit, volume gate settings, alert tolerances, shared negative lists.
4. **History**: change log export (what, when, who, why), last audit score and open findings.
5. **Open work**: running tests with read dates and what counts as a win, initiatives in flight and slated, paused shells (AI Max copies) and why.
6. **Risks**: anything fragile (shared budgets, expiring tokens, manual uploads, trademark limits).
7. **Access**: who holds admin on each platform, manager account links, billing owner; remove departing users only after the new owner confirms access. Never share credentials in the document.

## Output
A handoff document with those seven sections, plus a one-page "first week" list for the new owner.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_snapshot`, `paid_search_status`, `paid_search_audit`, `paid_search_proposals`.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_snapshot --out google_snapshot.json
   python3 scripts/run.py ads google_entities --out google.json
   python3 scripts/run.py ads microsoft_entities --out microsoft.json
   python3 scripts/run.py ads google_report change_history --days 28 --out changes.csv
   ```
3. **Your own data**: Editor exports, the change log and test log sheets.
