---
name: display-review
description: Weekly review of Google Demand Gen and Microsoft Audience ads - spend and results by placement, channel (YouTube in-stream, in-feed, Shorts, Discover, Gmail, Display Network, Microsoft Audience Network), audience and asset, frequency and lead quality, judged through the volume gate like search terms; proposes placement and audience exclusions, asset pauses, frequency caps and budget moves for a person to approve. Use for the weekly display check, when display brings junk leads or mobile app clicks, or when asked which placements to exclude.
license: MIT
compatibility: Any Agent Skills client. Math needs Python 3.10+, standard library only.
metadata:
  role: paid-display-manager
  stage: run
  cadence: Weekly
  summary: Placements, channels, audiences and assets through the volume gate; exclusions and budget moves to approve.
  needs: Connected Google and/or Microsoft accounts with 2+ weeks of display data; the goal conversion (a qualified stage) and its goal rate
---

# Display review

## Needs
Two or more weeks of display data by placement, channel, audience and asset; the goal conversion (a
qualified stage, not raw form fills) and its goal conversion rate; frequency per campaign.

## If something is missing
No goal rate? Ask; never assume one. Lead quality not connected? Judge on the platform conversion and say
it's a weaker signal.

## Method
1. **Placements like search terms**: each placement through the volume gate on the goal conversion (`placements`). Past the click line and below goal = exclude; 3+ conversions at goal = keep; otherwise hold. Biggest waste first. Mobile apps and games are the usual leak on the Display Network.
2. **Channels**: the same gate on each Demand Gen channel; a channel that fails gets its own ad group or is switched off in channel controls.
3. **Audiences and assets**: same gate; pause the losers, keep at least one live per ad group.
4. **Frequency**: over the cap (default 5 a week for retargeting, 3 for prospecting) = propose a cap.
5. **Budget moves**: against the scorecard (cost to reach in band, brand lift, pipeline). Retargeting never above its cap.
6. **Every change is a proposal** with its reason; the app applies it after approval and reads it back. Exclusions go on the shared account list.

## Output
A table: placement (or channel, audience, asset), spend, share of spend, clicks, conversions, action,
reason. Then the exclusions and moves to approve, and the wasted spend they stop.

## Getting the data
1. **Redavio connector**: `paid_display_report` (placements, channels, audiences, assets, reach, demographics) and `paid_display_review` (the gate, with proposals queued for approval).
2. **Your own API access**:
   ```
   python3 scripts/run.py ads google_report dg_placements --days 28 --out placements.csv
   python3 scripts/run.py ads microsoft_report audience_placements --days 28 --out placements_ms.csv
   python3 scripts/run.py perfos placements --input placements.csv --goal-cvr 0.02
   ```
