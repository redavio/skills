---
name: chatgpt-context-hints
description: "Build ChatGPT ads targeting: turn a keyword list or a search terms report into context hints and exclusions for each ad group, grouped and named by the same topic clusters as paid search, SEO and AEO, then check them against OpenAI's limits. Use when setting up ChatGPT ads targeting, when someone asks what to target in ChatGPT, or when an ad group's hints need tightening."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; pulling data needs your own OpenAI Ads API key.
metadata:
  role: chatgpt-ads-specialist
  stage: set-up
  cadence: Once at setup, then monthly
  summary: Turn keywords and search terms into context hints per ad group, each tagged with its topic cluster.
  needs: Keywords or a search terms export with conversions; the product and ICP; topic clusters from paid search
---

# Context hints

ChatGPT has no keywords. Each ad group gets up to 2,000 *context hints*: plain phrases describing conversations it should show in. OpenAI matches them loosely, so a tight theme per ad group beats a long list.

## Needs
- What you sell and who to (ICP), and the problems you solve in the buyer's words.
- Keywords or a search terms report (with conversions) from paid search.
- Topic clusters: the names paid search, SEO and AEO already use (e.g. forecasting, attribution).

## If something is missing
No search data: ask for the top 5 problems customers describe on sales calls and build hints from those. No clusters: propose them from the keywords and ask for a yes before using the names.

## Method
1. **One ad group per topic cluster**, named so its cluster is obvious. The cluster name must match paid search's exactly, so the channels can be compared topic by topic later.
2. **Hints from what converts**: start from converting search terms and keywords, rewritten as the question or task a buyer would bring to ChatGPT ("how do I forecast pipeline from ad spend"), plus the plain phrase ("pipeline forecasting software"). 20-60 per group is plenty to start.
3. **Leave out** brand terms of others unless it's a competitor ad group, jobs, free, login, support, and anything search has cut as a negative.
4. **Check them** (cleans match-type syntax, removes duplicates, enforces the limit and the cluster):
   ```
   python3 scripts/run.py perfos chatgpt-hints --input hints.json
   ```
   `hints.json`: `[{"ad_group": "Pipeline forecasting", "cluster": "forecasting", "hints": ["..."]}]`
5. **Monthly**: cut hints from ad groups chatgpt-weekly marks cut; add phrases from new converting search terms.

## Output
Per ad group: the cluster, the hints (cleaned), what was left out and why, and any problems from the check. Proposals only; a person adds them in Ads Manager or through chatgpt-build.

## Getting the data
1. **Your own API key** (read only; Ads Manager > Settings > General > API Keys, one per ad account): `export OPENAI_ADS_API_KEY=...` then `python3 scripts/run.py ads chatgpt_report ad_groups` for the current hints.
2. **Your own data**: a search terms CSV from Google or Microsoft, or a keyword list pasted in chat.
