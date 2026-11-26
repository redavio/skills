---
name: linkedin-ad-copy
description: "Write and check LinkedIn ads for B2B SaaS: single image, video, document and Thought Leader formats, checked against LinkedIn's limits (intro text 600 characters with about 150 shown, headline 200 with about 70 shown, LinkedIn's call-to-action list), plus the standard UTMs on every landing page. Use when writing, reviewing or refreshing LinkedIn ad copy."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; reading LinkedIn needs the Redavio connector or a Campaign Manager export.
metadata:
  role: linkedin-ads-manager
  stage: set-up
  cadence: At setup, then when creative fatigues
  summary: "Ads for every LinkedIn format, checked against LinkedIn's limits and the UTM standard before they're built."
  needs: "The offer, the audience (target accounts, ICP or engaged), the landing page, and any current ads"
---

# LinkedIn ad copy

One message per campaign, written for each format, then checked so nothing bounces or gets cut off on screen.

## Needs
- What's offered and to whom (the campaign: target accounts, ICP or engaged).
- The landing page.
- Optional: current ads to review.

## If something is missing
No offer: ask for the one thing the ad should make someone do (demo, trial, guide). No landing page: ask; ads can't be built without one.

## Method
1. **Write per format**: single image and video get an intro (keep the point in the first 150 characters) and a headline (under 70); a document ad gets an intro and the document; a Thought Leader ad uses a person's existing post, so there's no copy to write.
2. **Match the campaign**: target accounts and ICP sell the problem (awareness); engaged sells the next step (demo, trial).
3. **Check every ad** (don't eyeball it):
   ```
   python3 scripts/run.py perfos linkedin-ad --input ads.json
   ```
   Errors block the build; warnings mean text will be cut off.
4. **Fix and re-check** until there are no errors.

## Output
Each ad: format, intro, headline, CTA, landing page with UTMs, then its check (errors, warnings). Copy goes into the client's creative; the build uses it.

## Getting the data
1. **Through the Redavio connector** (app.redavio.com/mcp, LinkedIn connected): `paid_linkedin_plan` returns the current creative and landing page; the document ad's PDF is made in the Client Portal (Build > LinkedIn).
2. **Your own data**: a Campaign Manager export with the same columns, or numbers pasted in chat. Nothing in this skill writes to LinkedIn.
