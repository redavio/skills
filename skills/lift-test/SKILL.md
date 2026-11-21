---
name: lift-test
description: Prove whether display, video or retargeting causes lift - size a geo or audience holdout before launch (the smallest lift it can read at 95% confidence), say "not enough to test" when it can't be read, then read it with a difference in differences on branded search, direct traffic or pipeline in the test vs held-back regions. Uses Google Conversion Lift or Brand Lift results where the account is eligible. Use before launching Demand Gen or Microsoft Audience ads, when deciding whether retargeting earns its budget, or when asked whether display works.
license: MIT
compatibility: Any Agent Skills client. Math needs Python 3.10+, standard library only.
metadata:
  role: paid-display-manager
  stage: run
  cadence: Before launch, then at the read date
  summary: Holdout sized before launch and read at 95%; honest "not enough to test" when it can't be.
  needs: 14+ days of the lift metric (branded searches, direct visits or pipeline) by region; the expected lift; for the read, test and held-back daily values before and during
---

# Lift test

## Needs
To design: 14+ days of the lift metric (branded searches is the default), the lift you expect, and how
long you can run. To read: daily values for test and held-back regions, before and during the test.

## If something is missing
No expected lift? Use 10% for prospecting and 5% for retargeting, and say so. Fewer than 14 days of
history? Wait; don't guess the noise.

## Method
1. **Design before launch** (`lift-design`): the smallest readable lift at 95% confidence and 80% power from the metric's daily noise. If the expected lift is smaller, the answer is "not enough to test": run directional (scorecard brand lift) instead.
2. **Set the holdout at launch**: held-back regions (or an audience) that never see the ads, matched to the test regions on the metric. Microsoft has no lift studies, so it's always a geo holdout. Google Conversion Lift or Brand Lift where the account qualifies.
3. **Don't peek**: read at the read date only.
4. **Read** (`lift-read`): difference in differences on the daily log ratio test/held-back, two-sided. 95% = lift (or negative); below = no lift.
5. **Decide**: lift = keep and scale within the budget ladder; no lift = cut to frequency-capped reminders or off. Retargeting stays only with lift.

## Output
Design: minimum readable lift, verdict, read date, holdout regions. Read: lift, confidence, verdict, one
plain sentence ("Test regions +14% branded search against the holdout at 99% confidence: lift.").

## Getting the data
1. **Redavio connector**: `paid_display_lift` (design or read; reads branded search by region from the account).
2. **Your own API access**:
   ```
   python3 scripts/run.py perfos lift-design --input branded_daily.json --expected-lift 0.10 --test-days 28
   python3 scripts/run.py perfos lift-read --input holdout.json
   ```
