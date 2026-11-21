---
name: chatgpt-ad-copy
description: "Write ChatGPT chat card ads for B2B SaaS: titles of 3-50 characters, bodies up to 100, a crawlable landing page and an image at least 640 x 640, matched to each ad group's context hints, then check every ad against OpenAI's limits. Use when writing or refreshing ChatGPT ads, or when an ad was rejected or is over a limit."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; pulling data needs your own OpenAI Ads API key.
metadata:
  role: chatgpt-ads-specialist
  stage: set-up
  cadence: Once at setup, then monthly
  summary: Write chat card ads for each ad group and check every title, body, link and image against OpenAI's limits.
  needs: The ad group's topic and hints; your positioning and proof points; landing page URLs; images (640 x 640 or larger)
---

# ChatGPT ad copy

A chat card shows under a ChatGPT answer: title, body, image, link. The person just asked a question, so the ad should read like the next useful step, not a banner.

## Needs
- Per ad group: its topic and hints.
- Positioning, proof points (numbers you can stand behind), the offer (demo, trial, template).
- Landing page per ad group (https, crawlable by OpenAI) and images: JPEG, PNG or WebP, at least 640 x 640; 4-6 square images for a multi-image card where enabled.

## If something is missing
Ask for the offer first; without it there's no ad. No images: say what's needed and write the copy anyway.

## Method
1. **2-3 ads per ad group**, each a different angle: the outcome, the proof, the offer.
2. **Title (3-50 characters)**: the answer to the buyer's question, not your brand. **Body (up to 100)**: one proof point and the next step.
3. **Landing page** matches the ad group's topic; never the home page.
4. **Check every ad** (run it, don't count by hand):
   ```
   python3 scripts/run.py perfos chatgpt-card --input ads.csv
   ```
   `ads.csv`: `ad, ad_group, title, body, target_url` (optional `images` in JSON input: `[{"width": 1080, "height": 1080}]`).
5. **Monthly**: replace the ad with the lowest CTR in each ad group once it has 1,000+ impressions.

## Output
A table per ad group: ad name, title (with its length), body (with its length), landing page, image, and the check result. Proposals only; a person adds them in Ads Manager or through chatgpt-build.

## Getting the data
1. **Your own API key** (read only; Ads Manager > Settings > General > API Keys, one per ad account): `export OPENAI_ADS_API_KEY=...` then `python3 scripts/run.py ads chatgpt_report insights --days 28 --out insights.csv` for which ad groups need new copy.
2. **Your own data**: the positioning doc, customer quotes and current search ads pasted in chat.
