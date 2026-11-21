---
name: chatgpt-measure
description: "Measure ChatGPT ads against Google Ads and Microsoft Ads for B2B SaaS: cost per conversion and cost per pipeline dollar for the same dates, with attribution windows lined up (ChatGPT counts 1-day view by default), and say whether ChatGPT earns more budget. Use for the monthly channel review, when someone asks how ChatGPT ads compare to search, or before moving budget between channels."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; pulling data needs your own OpenAI Ads API key.
metadata:
  role: chatgpt-ads-manager
  stage: review
  cadence: Monthly
  summary: ChatGPT next to Google and Microsoft on CPA and pipeline, with attribution windows lined up, and what ChatGPT added.
  needs: Spend, conversions and pipeline per channel for the same dates; each channel's attribution window
---

# ChatGPT ads measurement

ChatGPT gets budget the same way any channel does: by producing pipeline at a cost that beats or adds to search.

## Needs
- For the same dates, per channel: spend, conversions, pipeline (from the CRM, by source), and each channel's attribution window.

## If something is missing
No pipeline by channel: rank on CPA and say it's a weaker answer. Different dates: stop and ask for matching ones.

## Method
1. **Line up attribution**: ChatGPT defaults to 30-day click + 1-day view; Google and Microsoft count clicks. Pull ChatGPT with `--view-days 0` for this comparison.
2. **Run the comparison** (don't do it by hand):
   ```
   python3 scripts/run.py perfos chatgpt-compare --input channels.json
   ```
   `channels.json`: `[{"channel": "Google Ads", "spend": 20000, "conversions": 200, "pipeline": 400000, "click_window_days": 30, "view_window_days": 0}, ...]`
3. **By topic cluster** where you have it: the same cluster on ChatGPT and search shows whether ChatGPT reaches new buyers or the same ones.
4. **Caused, not just touched**: if chatgpt-test ran, use its lift; otherwise label the comparison as attributed, not incremental.

## Output
One table: channel, spend, conversions, CPA, pipeline, cost per pipeline dollar, ranked; the warnings (attribution, missing pipeline); and one line on whether ChatGPT earns more, the same or less budget next month. Proposals only.

## Getting the data
1. **Your own API key** (read only; Ads Manager > Settings > General > API Keys, one per ad account): `export OPENAI_ADS_API_KEY=...` then `python3 scripts/run.py ads chatgpt_report insights --days 30 --view-days 0 --out chatgpt.csv`.
2. **Your own data**: Google and Microsoft totals (or the exec-report skill), and pipeline by source from the CRM.
