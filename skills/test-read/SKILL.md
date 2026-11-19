---
name: test-read
description: Read a finished Google Ads or Microsoft Ads experiment (A/B test, campaign experiment, AI Max test, ad copy or landing page test) - two-proportion significance on the goal metric, a win only at 95% confidence, otherwise logged as learning - and record the decision; also back-tests ICE scores against results. Use when a test hits its read date, someone asks if a test won, whether a result is significant, or whether to roll out a change.
license: MIT
compatibility: Any Agent Skills client. Math needs Python 3.10+, standard library only.
metadata:
  role: paid-search-manager
  stage: run
  cadence: Weekly
  summary: Win at 95% confidence on the goal metric or it's learning; roll out, keep control, or log.
  needs: Control and test arms' clicks and conversions (goal metric) over the full test; the hypothesis and read date
---

# Test read

## Needs
Each arm's clicks and goal conversions for the whole test (and value or cost if the goal is ROAS or CPA),
the hypothesis, start and read dates.

## If something is missing
Before the read date? Say so and don't call it: peeking inflates false wins. Missing an arm's numbers? Ask for them; never estimate.

## Method
1. **Judge on the campaign's goal metric**, as deep in the funnel as data is reliable (qualified stage or value over raw leads).
2. **Significance**: two-proportion z-test on conversion rate, two-sided. **95% confidence = win or loss.** Below that = inconclusive: logged as learning, not rolled out.
3. **Check the cost side** for CPA / ROAS goals: a higher conversion rate at a much higher CPC can still lose on CPA; report both.
4. **Decision**: won -> roll out (a change through change-safety); lost -> keep the control; inconclusive -> log, consider a bigger change or longer test.
5. **Log**: hypothesis, metric, ICE, start and read date, result, confidence, decision.
6. **Quarterly back-test**: do high ICE scores win more often (top third vs the rest)? Adjust scoring.

## Output
Control vs test (clicks, conversions, rate, CPA or ROAS), lift, confidence, verdict, decision, one
sentence in plain words: "AI Max arm converted 21% better at 97% confidence on qualified leads: roll out."

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_test_read` reads a test from the account.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py perfos test-read --control-conversions 40 --control-clicks 1000 --test-conversions 58 --test-clicks 1000
   python3 scripts/run.py perfos ice --input finished_tests.json     # back-test, with "status": won/lost/inconclusive
   python3 scripts/run.py ads google_report gaql --query "SELECT campaign.name, metrics.clicks, metrics.conversions FROM campaign WHERE segments.date BETWEEN '2026-10-01' AND '2026-10-28'"
   ```
3. **Your own data**: the experiment's results table from the platform UI, pasted in chat.
