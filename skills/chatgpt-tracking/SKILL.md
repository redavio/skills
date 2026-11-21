---
name: chatgpt-tracking
description: "Plan ChatGPT ads conversion tracking for B2B SaaS: the OpenAI pixel and Conversions API events mapped to CRM stages (lead, trial, demo, opportunity), deduplication between the two, which event is the goal, and the attribution window to use. Use when setting up tracking for ChatGPT ads, when conversions look wrong, or before switching to conversion bidding."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; pulling data needs your own OpenAI Ads API key.
metadata:
  role: chatgpt-ads-specialist
  stage: set-up
  cadence: Once at setup
  summary: Set up the OpenAI pixel and Conversions API events mapped to CRM stages, with deduplication and the attribution window.
  needs: Your CRM stages and which one is the goal; site access to add a script; server access for the Conversions API
---

# ChatGPT ads tracking

Without tracking, ChatGPT can only be judged on clicks. With it, it can be judged on pipeline, next to search.

## Needs
- CRM stages and the goal stage (a qualified one, not a raw form fill, where volume allows).
- Who can add a script to the site, and who can send server events.
- The pixel ID (Ads Manager > conversions tab).

## If something is missing
No server access: start with the pixel only and say pipeline stages will need the Conversions API later.

## Method
1. **Map stages to OpenAI's standard events**: form fill = `lead_created`, sign-up = `registration_completed`, trial = `trial_started`, demo booked = `appointment_scheduled`, paid = `subscription_created`. Only standard events can be a bidding goal; custom events are for reporting.
2. **Pixel** on every page (`oaiq("init", {pixelId})`, then `oaiq("measure", "lead_created", ...)` on the thank-you step). Respect consent: `oaiq("consent", false)` until the visitor agrees.
3. **Conversions API** for stages that happen later in the CRM (qualified lead, opportunity): POST to `https://bzr.openai.com/v1/events?pid=<PIXEL-ID>` from your server, with hashed email (SHA-256) and the `obref` click ID kept from the visit (cookie `__obref`). Events must be under 7 days old. Keep the Conversions API key on the server only.
4. **Deduplicate**: send the same event name and `id` from the pixel and the server for the same conversion.
5. **Attribution**: compare with search on the same footing. OpenAI defaults to 30-day click + 1-day view; for comparisons use 30-day click and view 0 (chatgpt-measure does this). Bidding and billing use clicks only.
6. **Check it works**: a test conversion shows in Ads Manager within a day. Some accounts need OpenAI to switch on Conversions API keys; a 403 means ask your OpenAI rep.

## Output
A tracking plan: stage-to-event table, where each fires (pixel or server), the goal event, dedupe rule, attribution settings, and the test to confirm it. Proposals only.

## Getting the data
1. **Your own API key** (read only; Ads Manager > Settings > General > API Keys, one per ad account): `export OPENAI_ADS_API_KEY=...` then `python3 scripts/run.py ads chatgpt_report account` to confirm the account and key.
2. **Your own data**: CRM stage list and the site's thank-you pages, pasted in chat.
