---
name: linkedin-plan
description: "Plan LinkedIn Ads for B2B SaaS: budget per campaign and ad set, a directional month of impressions and clicks, impressions per member per week, and audience size checks (LinkedIn needs 300 members to serve; under 50,000 delivers slowly). Use when someone asks how much to spend on LinkedIn, whether an audience is big enough, or before a LinkedIn build."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; reading LinkedIn needs the Redavio connector or a Campaign Manager export.
metadata:
  role: linkedin-ads-manager
  stage: set-up
  cadence: Once at setup, then quarterly
  summary: "Budget per campaign, the month it buys, and whether each audience is big enough to spend it."
  needs: "Each campaign's audience size and ad sets with daily budgets (paid_linkedin_report gives sizes); optional CPM and CTR"
---

# LinkedIn plan

A directional month per campaign, and the two checks that sink most LinkedIn plans: audiences too small to serve, and budgets that wear an audience out.

## Needs
- Each campaign: name, audience size in members, ad sets with daily budgets.
- Optional: your own CPM and CTR (defaults $35 and 0.5%).

## If something is missing
No audience sizes: call paid_linkedin_report (it returns them) or read them off Campaign Manager's forecast panel. No budget: start at LinkedIn's $10 a day per ad set.

## Method
1. **Get the sizes**: `paid_linkedin_report` returns each campaign's audience in members.
2. **Run the plan** (don't do it by hand):
   ```
   python3 scripts/run.py perfos linkedin-plan --input plan.json [--cpm 40 --ctr 0.006]
   ```
3. **Read the problems first**: under 300 members won't serve (widen it); under 50,000 delivers slowly (add titles, functions or accounts); over 3 impressions per member a week wears it out (lower the budget to the figure given, or widen).
4. **Target-accounts campaign**: small by design. Keep it, but size its budget to the frequency line, not to the ICP campaign's.

## Output
A table per campaign: members, daily and monthly budget, impressions, clicks, impressions per member per week. Then every problem with its fix, and the assumptions used. Directional: replace CPM and CTR with your own after 2-4 weeks.

## Getting the data
1. **Through the Redavio connector** (app.redavio.com/mcp, LinkedIn connected): `paid_linkedin_report` returns each campaign's audience size; `paid_linkedin_plan` returns the ad sets and budgets.
2. **Your own data**: a Campaign Manager export with the same columns, or numbers pasted in chat. Nothing in this skill writes to LinkedIn.
