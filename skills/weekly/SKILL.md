---
name: weekly
description: The weekly paid search loop for Google Ads and Microsoft Ads - runs prune-promote (approval queue across every lever), search-term-review, the AI Max and PMax review, parity-check, test-read and test-design, then exec-report for the weekly status, in that order. Use for a weekly review, weekly optimization, or "what should we change this week".
license: MIT
compatibility: Any Agent Skills client. Uses the job skills it calls.
metadata:
  role: paid-search-manager
  stage: cadence
  cadence: Weekly
  summary: Once a week: the queue, search terms, AI Max and PMax, parity, tests, the weekly report.
  needs: Account access or the last weeks of data; goals per segment; the test log
---

# Weekly

## Needs
Account access or the last 4-13 weeks of data, goals per segment, the test log. Missing goals: ask in chat.

## Steps
1. **prune-promote**: every lever that reached "act" on the volume gate, as a change list. The person approves or rejects each with a reason; approved changes go through **change-safety**.
2. **search-term-review**: cut and promote, whole weeks only.
3. **pmax-and-ai-max** (review part): AI Max search terms and chosen landing pages; PMax network split, search term insights, placements, lead quality by channel.
4. **parity-check**: Google vs Microsoft drift.
5. **test-read** for tests at their read date; **test-design** to keep the pipeline full (an ad copy test in every main ad group; next test by ICE).
6. **exec-report** (weekly): the table plus what we did, what's next, decisions needed.

## Output
The approved and rejected changes, the tests read and started, and the weekly report.

## Getting the data
(1) Redavio connector at `https://app.redavio.com/mcp` (`paid_search_proposals`, `paid_search_search_terms`, `paid_search_parity`, `paid_search_test_read`, `paid_search_performance`); (2) your own API access (Google Ads and Microsoft Advertising developer tokens plus your own OAuth app credentials for each; mode 1 needs none) with each job skill's scripts; (3) your own data.
