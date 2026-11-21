---
name: chatgpt-build
description: "Build a ChatGPT ads campaign from the agreed plan, context hints and chat card ads: everything checked against OpenAI's limits and created PAUSED, as a bulk mutation job (validate_only first) or step-by-step Ads Manager instructions. Use when someone says build the ChatGPT campaign, or the plan, hints and ads are agreed."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; pulling data needs your own OpenAI Ads API key.
metadata:
  role: chatgpt-ads-manager
  stage: set-up
  cadence: Once at setup, then per new campaign
  summary: Turn the agreed plan, hints and ads into one paused campaign, as a checked bulk request or click-by-click steps for Ads Manager.
  needs: The agreed plan (objective, budget, bid); hints and ads per ad group, each with its cluster; landing pages and image URLs
---

# ChatGPT ads build

Everything goes in paused. Nothing is sent by this skill: the person builds it in Ads Manager, or sends the checked request with their own key.

## Needs
- The agreed plan (chatgpt-plan): objective, daily or lifetime budget, bid, countries.
- Per ad group: name, cluster, hints (chatgpt-context-hints), ads (chatgpt-ad-copy) with a public https image URL.

## If something is missing
Ask for it; never fill a gap with a made-up bid, URL or image.

## Method
1. **Write the build file** (`build.json`):
   `{"campaign": {"name": "chatgpt|clicks|core|us|en", "objective": "clicks", "daily_budget": 100, "countries": ["US"]}, "ad_groups": [{"name": "Pipeline forecasting", "cluster": "forecasting", "max_cpc": 3.0, "hints": [...], "ads": [{"name": "...", "title": "...", "body": "...", "target_url": "https://...", "image_url": "https://..."}]}]}`
   Campaign names follow `channel|objective|theme|geo|language`.
2. **Check and build the request** (refuses anything that would bounce):
   ```
   python3 scripts/run.py perfos chatgpt-bulk --input build.json > job.json
   ```
   `job.json` is the body for `POST /bulk_mutation_jobs`: every campaign, ad group and ad `paused`, budgets and bids in micros, children linked by idempotency key, `validate_only: true`. It also lists each ad group's cluster; save that as `clusters.json` for reporting.
3. **Show the person the tree** (campaign > ad groups > hints count and ads) and get a yes.
4. **Two ways in, both theirs:** (a) build it by hand in Ads Manager from the tree, or (b) send `job.json` with their own key (OpenAI's bulk API is in limited preview; a 404 means it isn't on for the account), check the validation result, then send again with `validate_only: false`.
5. **Read it back**: `python3 scripts/run.py ads chatgpt_report campaigns` and `ad_groups`; everything should be paused with the right hints. Launching (un-pausing) is the person's click.

## Output
The campaign tree, the check result, `job.json` and `clusters.json`, and the read-back after they build it.

## Getting the data
1. **Your own API key** (read only; Ads Manager > Settings > General > API Keys, one per ad account): `export OPENAI_ADS_API_KEY=...` then `python3 scripts/run.py ads chatgpt_report campaigns` and `ad_groups` to read back what was built.
2. **Your own data**: the outputs of chatgpt-plan, chatgpt-context-hints and chatgpt-ad-copy.
