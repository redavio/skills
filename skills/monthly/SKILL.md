---
name: monthly
description: The monthly paid search loop for Google Ads and Microsoft Ads - runs diagnose on every gap to goal, exec-report for the monthly report, and budget-rebalance across campaign types on marginal return within the step limit, in that order. Use at month end, for a monthly review, monthly report, or monthly budget reallocation.
license: MIT
compatibility: Any Agent Skills client. Uses the job skills it calls.
metadata:
  role: paid-search-manager
  stage: cadence
  cadence: Monthly
  summary: Once a month: diagnose every gap, the monthly report, rebalance budget.
  needs: The month's and prior month's data; goals; budgets, impression share and the step limit
---

# Monthly

## Needs
The month's and prior period's data by segment and platform, goals, current budgets and impression share, the step limit. Missing goals or step limit: ask in chat.

## Steps
1. **diagnose** every row that missed goal (brand, non-brand, PMax, Google, Microsoft): tracking first, mix vs rate, lever split, the lever to pull.
2. **exec-report** (monthly): TL;DR, the table with a driver sentence per row, fix and press actions, initiatives.
3. **budget-rebalance**: moves on marginal return; within the step limit = routine, over it = client approval (change-safety).

## Output
Every gap with a named cause and next action, the report, and the budget proposals awaiting a yes.

## Getting the data
(1) Redavio connector at `https://app.redavio.com/mcp` (`paid_search_diagnose`, `paid_search_performance`, `paid_search_proposals`); (2) your own API access (Google Ads and Microsoft Advertising developer tokens plus your own OAuth app credentials for each; mode 1 needs none) with each job skill's scripts; (3) your own data.
