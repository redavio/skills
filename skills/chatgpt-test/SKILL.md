---
name: chatgpt-test
description: "Design and read a holdout test for ChatGPT ads: hold some regions (or an audience) out, size whether the test can detect the lift before launch, then read test vs held-back regions at the end. ChatGPT has no keywords to split, so this is how to prove it adds pipeline rather than taking credit for it. Use when someone asks whether ChatGPT ads really work, or before scaling ChatGPT spend."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; pulling data needs your own OpenAI Ads API key.
metadata:
  role: chatgpt-ads-specialist
  stage: run
  cadence: Before launch, then at the read date
  summary: "Prove whether ChatGPT ads add pipeline with a geo or audience holdout: size it before launch, read it at the end."
  needs: Daily values of the metric to move (pipeline, demo requests, branded searches) by region for 4+ weeks; the regions you can hold out
---

# ChatGPT ads test

Click attribution says what ChatGPT touched, not what it caused. A holdout answers the real question: would this pipeline have happened anyway?

## Needs
- Daily values of the metric to move (pipeline created, demo requests or branded searches), by region, 4+ weeks before.
- Regions you can run in and hold out (ChatGPT location targeting includes and excludes countries and regions).

## If something is missing
No regional data: use countries if you sell in several; otherwise say a holdout isn't possible and compare on CPA with chatgpt-measure, labelled as correlation.

## Method
1. **Size it before launch** (shared holdout math):
   ```
   python3 scripts/run.py perfos lift-design --input metric.json --expected-lift 0.10 --test-days 28
   ```
   "Not enough to test" means run longer, hold out more, or don't run the test.
2. **Set it up**: run in the test regions, exclude the held-back regions in the campaign's targeting. Keep every other channel the same in both.
3. **Read it at the date, not before**:
   ```
   python3 scripts/run.py perfos lift-read --input readout.json
   ```
   `readout.json`: `test_pre, test_post, control_pre, control_post` (daily lists).
4. **Decide**: a lift at 95% earns more budget; no lift means ChatGPT is taking credit for pipeline that would have come anyway.

## Output
Before: regions, length, metric, and whether the test can detect the expected lift. After: the lift, its confidence, and what to do with the budget. Proposals only.

## Getting the data
1. **Your own API key** (read only; Ads Manager > Settings > General > API Keys, one per ad account): `export OPENAI_ADS_API_KEY=...` then `python3 scripts/run.py ads chatgpt_report insights --days 56 --out insights.csv` for spend in the test period.
2. **Your own data**: pipeline by region from the CRM, or branded searches by region from Google Ads.
