---
name: chatgpt-plan
description: "Plan a ChatGPT ads test for a B2B SaaS company: pick the objective (impressions, clicks or conversions) and bid type, size the starting budget, forecast impressions, clicks, conversions and CPA from stated assumptions, and say when conversion bidding has enough data. Use when someone asks whether to try ChatGPT ads, how much to spend, which objective to pick, or what results to expect."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; pulling data needs your own OpenAI Ads API key.
metadata:
  role: chatgpt-ads-specialist
  stage: set-up
  cadence: Once before testing ChatGPT, then monthly
  summary: "Decide whether and how to test ChatGPT ads: objective, bid type, starting budget and a directional forecast, with a gate on conversion bidding."
  needs: Monthly budget you can test with; pipeline goal or target CPA; expected CTR and conversion rate (or search's as a start)
---

# ChatGPT ads plan

ChatGPT ads are new, so the plan is a test with a budget you can afford to learn with, not a forecast to hold anyone to.

## Needs
- Monthly test budget, and the pipeline goal or target CPA it answers to.
- Assumptions: CTR and conversion rate (start from search's non-brand landing-page rate if there's nothing else), and a CPM or CPC.
- Conversions from ChatGPT in the last 30 days, if any.

## If something is missing
Ask one question at a time. No CTR: use 0.7% and say it's an early third-party figure. No CPM: use OpenAI's $60 default. Never invent a goal.

## Method
1. **Objective.** B2B SaaS starts on **clicks** (you pay for visits, and the landing page does the work). Impressions only for awareness with a lift test (chatgpt-test). Conversions only once the gate passes.
2. **Run the math** (don't do it by hand):
   ```
   python3 scripts/run.py perfos chatgpt-plan --monthly-budget 3000 --objective clicks --cpc 2.50 --ctr 0.007 --cvr 0.02 --conversions-30d 0
   ```
   It returns impressions, clicks, conversions, CPA, the daily budget and the bid in micros ($2.50 = 2,500,000).
3. **Conversion bidding gate**: 30 conversions in 30 days, the same line as search targets. Below it the plan stays on clicks and says when to switch.
4. **Size the test to learn**: the budget must reach the volume gate for at least one ad group in 4 weeks; if it can't, cut ad groups, not the budget per group.
5. **Compare with search**: put the plan's CPA next to search non-brand CPA; ChatGPT earns more budget only by beating it or adding pipeline search can't reach.

## Output
A short plan: objective and why, monthly and daily budget, bid, the forecast table (impressions, clicks, conversions, CPA) with every assumption named, the conversion-bidding status, and the date to re-plan with real numbers (2-4 weeks in).

## Getting the data
1. **Your own API key** (read only; Ads Manager > Settings > General > API Keys, one per ad account): `export OPENAI_ADS_API_KEY=...` then `python3 scripts/run.py ads chatgpt_report insights --days 30 --out insights.csv` for real CTR, CPC and conversions.
2. **Your own data**: search's CTR and conversion rate, or numbers pasted in chat.
