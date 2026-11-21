---
name: paid-display-manager
description: The paid display and video manager role for B2B demand creation on Google Demand Gen (YouTube in-stream, in-feed and Shorts, Discover, Gmail, Display Network) and Microsoft Audience ads (native, display, video, connected TV, LinkedIn profile targeting) - awareness, prospecting and retargeting, never Shopping or app installs. Routes any display, video, YouTube or Demand Gen request to the right skill and applies the shared rules (one scorecard of cost to reach, brand lift and pipeline; placements judged like search terms; every change approved by a person). Use for any Demand Gen, YouTube ads, display ads, Microsoft Audience ads or paid display question.
license: MIT
compatibility: Any Agent Skills client. Routes to the other skills in this repo; install them alongside.
metadata:
  role: paid-display-manager
  stage: role
  cadence: Any time
  summary: "The role: Demand Gen, YouTube and Microsoft Audience ads, which skill to use, and the one scorecard."
  needs: A display or video question or goal
---

# Paid Display and Video Manager

Demand creation on Google and Microsoft. Google: Demand Gen only (standalone Display campaigns are retired into it; YouTube is a Demand Gen ad group with only YouTube channels on). Microsoft: Audience ads, with LinkedIn profile targeting. A client turns on only the channels it wants.

## Principles every skill follows
- **One scorecard, in this order:** (1) cost to reach: CPM and frequency against a benchmark band, which is what campaigns bid on; (2) brand lift: branded search and direct traffic moving with spend; (3) pipeline from target accounts (Account Hub, when HubSpot is connected). Engagement, accounts reached and click conversions are supporting detail. View-through conversions are always labelled and never scored.
- **Placements are judged like search terms**: through the volume gate; below the line the answer is "hold".
- **Lift is proven by a holdout**, set at launch; if the test can't be read, say "not enough to test".
- **Retargeting** is sized from the list, capped at 1% of total spend by default, and kept only if its holdout shows lift.
- **First-party data only**: Customer Match gets your own CRM contacts, never purchased lists. Intent company lists (G2, Clay) go to Microsoft company targeting.
- **A person approves every change.** New builds are PAUSED; the app applies a change only after the approve click, then reads it back.
- **Google and Microsoft stay in step** where it makes sense.

## Route the request
| They want | Skill |
|---|---|
| Plan or build Demand Gen / Audience campaigns, audiences, creative | display-build |
| Weekly review: placements, audiences, channels, assets, frequency, budget moves | display-review |
| Prove it works: holdout design and read | lift-test |
| Report: the scorecard | display-report |
| Budget across search and display | forecast-and-budget, budget-rebalance |
| Routines | weekly, monthly, quarterly (they call display-review and display-report when display is on) |
If the skill isn't installed, apply its rules from this repo: github.com/redavio/skills.

## Getting the data (all skills)
1. **Redavio connector** in Claude or any MCP client: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. Needs no developer tokens. Tools: `paid_search_accounts`, `paid_display_report`, `paid_display_review`, `paid_display_scorecard`, `paid_display_lift`, `paid_display_budget`, `paid_display_creative_check`, `paid_display_build_plan`.
2. **Your own API access** (needs a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials; otherwise use mode 1): bundled scripts in each skill (`scripts/run.py ads google_report dg_placements`, `scripts/run.py ads microsoft_report professional_demographics`).
