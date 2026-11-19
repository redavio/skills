---
name: target-math
description: Work out what target CPA or target ROAS a Google Ads or Microsoft Ads campaign should bid to, backed out from the business (LTV, target LTV:CAC, ACV, funnel stage rates), plus dollar values per funnel stage, when the account is ready to add a target, and the step path from current performance to the goal. Use when someone asks what their target CPA or ROAS should be, what a lead or stage is worth, when to switch from Maximize Conversions to a target, or how fast to tighten a target.
license: MIT
compatibility: Any Agent Skills client. The math needs Python 3.10+, standard library only.
metadata:
  role: paid-search-manager
  stage: set-up
  cadence: Once at setup, then quarterly
  summary: Target CPA or ROAS backed out from LTV, CAC ratio and stage rates; stage values; when and how to add a target.
  needs: LTV or ACV; target LTV:CAC; stage rates from the bid-on conversion to opportunity and won; current CPA or ROAS and last-30-day conversions for timing
---

# Target math

Every calculated number is a recommendation. A person can override it with a different goal; the
override wins and is recorded with who and why. A human sets the target in the platform.

## Needs
- LTV (or ACV and expected lifetime), target LTV:CAC (often 3), paid media's share of CAC (default all of it).
- Rates: bid-on conversion to opportunity (S2), opportunity to won; pipeline per conversion for ROAS.
- For timing: conversions in the last 30 days, current CPA or ROAS, the client's step limit.
- Weekly in-platform conversions and weekly opportunities (8+ weeks) to check they move together.

## If something is missing
Ask for the single number that blocks you ("What share of opportunities close?"). If they only have
industry guesses, run it and label every input that is a guess. Never present it as their number.

## Method
1. **Back out the most you can pay at each stage:**
   - max CAC = LTV / target LTV:CAC x media share
   - max cost per opportunity = max CAC x opportunity-to-won rate
   - **tCPA** (the conversion bid on) = max cost per opportunity x conversion-to-opportunity rate
   - **tROAS** = expected pipeline (or value) per conversion / max CPA, when conversion values are pipeline-based
2. **Trust check first**: in-platform conversions must track opportunities week to week (correlation 0.5+). If not, flag it before anyone uses the math: the bid-on conversion may be the wrong one.
3. **Stage values** (for value bidding): value = ACV x chance a record at that stage becomes a won deal. The stage bid on carries 2-3 value tiers by lead fit (high / mid / low by company size or ICP match); target ROAS needs values that vary.
4. **Ladder and timing**:
   - Value ladder: Maximize Conversion Value, then add target ROAS. Volume ladder: Maximize Conversions, then add target CPA. Switch volume to value once values have run ~4 weeks (or 3 conversion cycles); switching ladders is a strategy change, do it once.
   - No target at launch on a new campaign. Inherited campaigns with history can get one right away, near current performance.
   - Add the target at ~30 conversions in 30 days (tCPA) or Google's floor of 15 conversions with values (tROAS). Microsoft: 30 before judging.
   - First target near current performance, not the goal; tighten in steps no bigger than the step limit. Adding the first target triggers Learning (up to 7 days); later target changes don't.
5. One objective per campaign: conversions, CPA, conversion value or ROAS.

## Output
The chain as lines with the math shown ("LTV $60,000 / 3 = max CAC $20,000 ... = tCPA $500"), the
trust check result, stage values, whether it's ready for a target, and the step path
("$260 now -> $221 -> $188 -> $180 goal"). End with: "Recommendation; set it in the platform yourself or approve it."

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_target_math` runs this from the intake; `paid_search_performance` gives current CPA, ROAS and conversions.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py perfos targets --ltv 60000 --ltv-to-cac 3 --s2-to-won 0.25 --conv-to-s2 0.10 --weekly-conversions "[10,12,9,15,11,13,12,14]" --weekly-s2s "[1,1.2,0.9,1.5,1.1,1.3,1.2,1.4]"
   python3 scripts/run.py perfos stage-values --acv 30000 --rates '{"demo": 0.04, "sql": 0.12, "opportunity": 0.25}'
   python3 scripts/run.py perfos ready --conversions-30d 22 --kind tcpa
   python3 scripts/run.py perfos first-target --current 260 --goal 180 --step-limit 0.15
   ```
   Current CPA and conversions: `python3 scripts/run.py ads google_report campaign_daily --days 30`.
3. **Your own data**: CRM stage counts and deal values in a sheet; paste the rates in chat.
