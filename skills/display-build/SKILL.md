---
name: display-build
description: Plan and build Google Demand Gen and Microsoft Audience ads campaigns for B2B awareness, prospecting and retargeting - goal per campaign, channel controls (YouTube in-stream, in-feed, Shorts, Discover, Gmail, Maps, Display Network), audiences from the ICP (Customer Match from your CRM, lookalikes, custom segments, site and video retargeting, LinkedIn profile targeting on Microsoft), exclusions, frequency caps, bidding by goal, the shared placement exclusion list, reach and retargeting budgets, and creative for every format checked against specs. Everything built PAUSED after approval. Use when launching Demand Gen, YouTube or Microsoft Audience campaigns, or adding display to a search account.
license: MIT
compatibility: Any Agent Skills client. Math needs Python 3.10+, standard library only.
metadata:
  role: paid-display-manager
  stage: set-up
  cadence: Once at setup, then per new campaign
  summary: Demand Gen and Microsoft Audience campaigns planned, creative made for every format, built paused after your yes.
  needs: ICP (industries, sizes, roles, target accounts); the goal per campaign; audience size or list sizes; total monthly spend; brand assets (logo, colours, product); HubSpot for Customer Match
---

# Display build

## Needs
The ICP and target account list, each campaign's goal (awareness, prospecting, retargeting), list sizes
(site visitors, video viewers, CRM contacts), total monthly paid spend, the brand (name, logo, colours,
product, proof points), and which channels the client wants on.

## If something is missing
Ask for the goal first: it decides the bidding. No creative? Make it (see Creative). No target account
list? Build from the ICP with native audiences and say coverage can't be scored yet.

## Method
1. **When**: capture before creation. Prospecting display and video once measurable search is maxed (around $250k a month on the budget ladder); retargeting as soon as the list can serve. Recommend, never block.
2. **Structure**: one campaign per goal. Google: Demand Gen. Ad groups split by channel set when channels behave differently: YouTube-only (in-stream, in-feed, Shorts), Google-owned (YouTube, Discover, Gmail), Display Network. Microsoft: Audience campaigns, one ad group per audience.
3. **Audiences**: Customer Match from your own CRM contacts (target accounts' people), lookalikes from it, custom segments (competitor names, G2 category terms, competitor sites), in-market; Microsoft LinkedIn profile targeting (company up to 1,000 per ad group, industry, job function, seniority; US, CA, UK, AU, FR, DE). Retargeting: site visitors and video viewers. Exclude customers, employees and recent converters. Customer Match targeting on Google needs 90 days and $50,000 lifetime spend; below that, observation and exclusions only, and say why.
4. **Bidding by goal**: awareness and prospecting on CPM or cost per view (target CPC replaces manual CPC in Demand Gen); retargeting on conversions only with the volume. Frequency caps on every campaign.
5. **Budgets**: reach budget = audience x reach share x frequency x CPM (`reach-budget`); retargeting sized from the list and capped at 1% of total spend (`retargeting-budget`).
6. **Brand safety**: the account-level placement exclusion list (shared with PMax), junk app categories, standard content suitability.
7. **Creative, for every format**: Demand Gen images 1.91:1, 1:1, 4:5 and a 1:1 logo; carousels of 2 to 10 cards; video 16:9 (in-stream), 1:1 or 9:16 (in-feed), 9:16 (Shorts, hook in the first 2 seconds); headlines 40, descriptions 90 characters. Microsoft: 1.91:1 and 1:1 images, short headline 30, long headline 90, video. Images from an image model (state the cost first); video from images, voice, captions and music. Check every asset with `creative-check`.
8. **Holdout at launch** if lift will be tested: run `lift-test` before launch and hold back its regions.
9. **Build**: propose the plan; after the person's yes the app builds it PAUSED on Google and Microsoft and reads it back.

## Output
A plan per campaign: goal, channels, audiences, exclusions, bidding, frequency cap, budget, creative list
with spec checks, holdout. Then the build proposal for approval.

## Getting the data
1. **Redavio connector**: `paid_display_budget` (reach and retargeting), `paid_display_creative_check`, `paid_display_build_plan` (queues the paused build for approval in the app).
2. **Your own API access**:
   ```
   python3 scripts/run.py perfos reach-budget --audience 200000 --reach-share 0.5 --frequency 4 --cpm 10
   python3 scripts/run.py perfos retargeting-budget --list-size 20000 --weekly-frequency 3 --cpm 10 --total-monthly-spend 100000
   python3 scripts/run.py perfos creative-check --input assets.json --platform google
   ```
