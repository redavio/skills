---
name: paid-search-manager
description: The paid search manager role for B2B demand capture on Google Ads and Microsoft Ads (Search, AI Max, Performance Max) - explains the full skill set from intake to audit and routes any paid search request to the right skill, applying the playbook's principles (judge on business goals, let the data decide through the volume gate, every change approved by a person). Use for any Google Ads, Microsoft Ads, Bing Ads, PPC or paid search question when no more specific skill is obviously right, or when someone asks what these skills can do.
license: MIT
compatibility: Any Agent Skills client. Routes to the other skills in this repo; install them alongside.
metadata:
  role: paid-search-manager
  stage: role
  cadence: Any time
  summary: The role: what each skill does and which one to use, with the principles they share.
  needs: A paid search question or goal
---

# Paid search manager

Demand capture on Google and Microsoft: Search, AI Max, Performance Max. Every job skill works on its own; this one picks the right one.

## Principles every skill follows
- **Judge against business goals** (pipeline, not clicks). One objective per campaign: conversions, CPA, conversion value or ROAS. Brand and non-brand always separate.
- **Let the data decide**: the volume gate decides when there's enough data; below it the answer is "watch".
- **Deterministic math**: every number comes from the scripts or the data, never from memory.
- **A person approves every change.** Dry run first, apply one change on an explicit yes, read it back. New builds are created PAUSED.
- **Ask, don't stop**: if an input is missing (e.g. the CPA goal), ask in chat.

## Route the request
| They want | Skill |
|---|---|
| Where things stand, what's next | status |
| Start a new account or client | intake |
| Keywords | keyword-research |
| How much to spend, budget split, scenarios | forecast-and-budget |
| What tCPA / tROAS should be, stage values | target-math |
| Conversion tracking, offline conversions | tracking-plan |
| Account structure, naming | campaign-structure |
| Negatives, cannibalization, brand leakage | negatives-and-fencing |
| Ads and extensions | ad-copy |
| PMax, AI Max, audience signals | pmax-and-ai-max |
| Push a plan to Google (paused) | build |
| Go live | launch-check |
| Pacing, alerts, morning check | pacing-and-alerts |
| Search terms | search-term-review |
| Enough data to call it? | volume-gate |
| What to pause or scale across levers | prune-promote |
| Move budget between campaigns | budget-rebalance |
| Make any change safely, what changed | change-safety |
| Google vs Microsoft drift | parity-check |
| What to test, test sizing | test-design |
| Did the test win | test-read |
| Where to grow | expansion-finder |
| Why a number moved | diagnose |
| Weekly or monthly report | exec-report |
| Account audit | audit |
| Quarterly review and re-plan | qbr |
| Hand the account over | handoff |
| Routines | daily, weekly, monthly, quarterly |
If the skill isn't installed, apply its rules from this repo: github.com/redavio/skills.

## Getting the data (all skills)
1. **Redavio connector** in Claude or any MCP client: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. Needs no developer tokens. Tools: `paid_search_accounts`, `paid_search_snapshot`, `paid_search_performance`, `paid_search_search_terms`, `paid_search_audit`, `paid_search_volume_gate`, `paid_search_diagnose`, `paid_search_forecast`, `paid_search_target_math`, `paid_search_test_read`, `paid_search_parity`, `paid_search_proposals`, `paid_search_status`.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens): bundled scripts in each skill (`scripts/run.py ads ...`).
3. **Your own data**: CSVs, exports or a Google Sheet; the math runs on them (`scripts/run.py perfos ...`).
