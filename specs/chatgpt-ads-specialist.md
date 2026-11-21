# ChatGPT Ads Specialist spec

Agreed 2026-11-21. Source for OpenAI's platform: https://developers.openai.com/ads/llms.txt (read 2026-11-21).

## Goal
Run ChatGPT ads for a B2B SaaS company the way the Paid Search Manager runs search: plan, build, optimize, test and measure, with every change approved by a person. OpenAI's own app does the clicking inside ChatGPT; these skills are the B2B SaaS method around it (plan to pipeline, measured against Google and Microsoft, tests) and work in any AI app.

## Who uses it
A paid search or performance marketer adding ChatGPT as a channel: deciding whether to test it, building the first campaign, and in the weekly and monthly reviews after launch.

## What OpenAI offers (2026-11-21)
- Formats: chat card (title 3-50 characters, body up to 100, image at least 640 x 640; 4-6 square images on some accounts) and product feed ads.
- Targeting: no keywords; up to 2,000 context hints per ad group (not exact match), locations, platforms, custom audiences (25,000 matched users to target).
- Buying: Campaign > Ad group > Ad. Objectives impressions (bid per impression, $60 CPM default), clicks, conversions (billed per click, needs a pixel event). Everything is created paused.
- API: read and write at https://api.ads.openai.com/v1, one key per ad account, keys can't be limited to reading. Insights by account, campaign, ad group and ad. Bulk jobs in limited preview. No file import in Ads Manager.
- Tracking: pixel and Conversions API; 30-day click and 1-day view by default; billing and optimization on clicks only.

## Skills
- Plan: chatgpt-ads-specialist (role guide), chatgpt-plan.
- Build: chatgpt-context-hints, chatgpt-ad-copy, chatgpt-tracking, chatgpt-build.
- Optimize: chatgpt-weekly. Test: chatgpt-test. Measure: chatgpt-measure.

## Inputs and outputs
- Inputs: plan assumptions; keywords or search terms; positioning and landing pages; ad group insights from the user's own key (`chatgpt_report.py`, GET only) or an export; other channels' spend, conversions and pipeline.
- Outputs: a plan, hints per ad group, checked ads, a tracking plan, a paused and checked bulk request (plus Ads Manager steps), a weekly action list, a holdout design and read-out, a channel comparison.
- Code: `shared/perfos/chatgpt.py` (limits, plan math, weekly review, bulk job, comparison) and `shared/ads_scripts/_chatgpt.py` + `chatgpt_report.py` (read-only client). The AI writes and judges; the code does the math and the checks.
- One topic key across channels: every ad group carries a topic cluster name, the same one its paid search ad group, SEO and AEO cluster use, so channels can be joined by topic later.

## Planted signal
In `shared/examples/chatgpt_insights.csv`, the ad group with broad hints ("Broad - AI tools") runs at 3x the account's CPA, and in `chatgpt_ads.csv` one title is 54 characters. `chatgpt-weekly` flags both and nothing else.

## Done when
- The planted signal is found and the noise is not; bad input gives a plain-English error; empty data says so.
- Tests green on GitHub; build_index.py leaves no diff.
- Runs in the user's AI app through the Redavio MCP server, same results as the repo.
- Library card, its own channel on the homepage workflow, a page per skill, video and screenshots.

## Not doing
- Product feed ads (shopping, not B2B SaaS).
- Any create, change or pause sent to OpenAI by the skills or the MCP server.
- A Redavio app connector or Client Portal panel (later, its own spec).
- Custom audience uploads.
