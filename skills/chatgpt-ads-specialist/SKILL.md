---
name: chatgpt-ads-specialist
description: The ChatGPT ads specialist role for B2B SaaS on OpenAI's ad platform (ads in ChatGPT answers) - explains the skill set from plan to measurement and routes any ChatGPT ads request to the right skill, applying the same principles as paid search (judge on pipeline, let the data decide, every change approved by a person). Use for any ChatGPT ads, OpenAI ads, Ads Manager, context hints or chat card question when no more specific skill is obviously right, or when someone asks what these skills can do.
license: MIT
compatibility: Any Agent Skills client. Routes to the other chatgpt-* skills in this repo; install them alongside.
metadata:
  role: chatgpt-ads-specialist
  stage: role
  cadence: Any time
  summary: "The role: what each ChatGPT ads skill does and which one to use, with the principles they share."
  needs: A ChatGPT ads question or goal
---

# ChatGPT ads specialist

Ads in ChatGPT answers, bought in OpenAI's Ads Manager. Every job skill works on its own; this one picks the right one.

## How ChatGPT ads differ from search
- **No keywords.** Each ad group gets up to 2,000 *context hints*: plain phrases describing the conversations it should show in. Hints are not exact match, so tight themes matter more than long lists.
- **One format for B2B: the chat card** (title 3-50 characters, body up to 100, an image at least 640 x 640, a landing page).
- **Three objectives**: impressions (bid per impression, $60 CPM default), clicks (CPC), conversions (needs an active pixel event; still billed per click). Everything is created paused.
- **Reporting** by account, campaign, ad group and ad, split by country, device or platform. Default attribution: 30-day click and 1-day view. OpenAI bills and optimizes on clicks only.
- **One API key per ad account**, made in Ads Manager > Settings > General > API Keys. It can't be limited to reading, so these skills only ever read with it.

## Principles every skill follows
- **Judge against business goals** (pipeline, not clicks), and next to search: ChatGPT earns budget by beating or adding to Google and Microsoft.
- **One topic cluster name per ad group**, the same name its paid search ad group, SEO and AEO cluster use, so every channel can be compared topic by topic.
- **Let the data decide**: the volume gate decides when there's enough data; below it the answer is "watch".
- **Deterministic math**: every number comes from the scripts or the data, never from memory.
- **A person approves every change.** These skills propose; a person makes the change in Ads Manager.
- **Ask, don't stop**: if an input is missing, ask in chat.

## Route the request
| They want | Skill |
|---|---|
| Should we test ChatGPT, how much, which objective | chatgpt-plan |
| What to target (hints) | chatgpt-context-hints |
| Ads | chatgpt-ad-copy |
| Pixel, Conversions API, attribution window | chatgpt-tracking |
| Build the campaign (paused) | chatgpt-build |
| Weekly review, what to cut or scale | chatgpt-weekly |
| Prove ChatGPT adds pipeline (holdout) | chatgpt-test |
| ChatGPT vs Google and Microsoft | chatgpt-measure |

## Getting the data
1. **Your own API key** (read only): set `OPENAI_ADS_API_KEY`; each job skill's `scripts/run.py` pulls the report it needs.
2. **Your own data**: an Ads Manager export, or numbers pasted in chat.
