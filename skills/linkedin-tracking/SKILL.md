---
name: linkedin-tracking
description: "Check LinkedIn tracking for B2B SaaS: the Insight Tag on the site (after advertising consent), at least one conversion (signup or demo) for the engaged campaign, and the standard UTMs on every landing page (source linkedin, medium paid_social). Use before a LinkedIn launch, when LinkedIn conversions look wrong, or when checking UTMs."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; reading LinkedIn needs the Redavio connector or a Campaign Manager export.
metadata:
  role: linkedin-ads-manager
  stage: set-up
  cadence: Once at setup, then after any site change
  summary: "Insight Tag, conversions and UTMs checked before any money is spent on LinkedIn."
  needs: "The Insight Tag partner ID, the conversions set up, and the live landing-page URLs"
---

# LinkedIn tracking

Three things must be right before a LinkedIn dollar is spent: the Insight Tag, a conversion, and UTMs that match the naming standard.

## Needs
- The Insight Tag partner ID and whether it fires on the site.
- The conversions defined in Campaign Manager.
- The landing-page URLs per campaign.

## If something is missing
No Insight Tag: Campaign Manager > Analyze > Insight Tag, then add it to the site behind advertising consent. No conversion: add one for the signup or demo page.

## Method
1. **Collect the setup** into tracking.json: insight_tag, tag_on_site, conversions, landing_urls (campaign, url).
2. **Run the check**:
   ```
   python3 scripts/run.py perfos linkedin-tracking --input tracking.json
   ```
3. **UTMs**: source `linkedin`, medium `paid_social`, campaign = the campaign name with `|` as `-`, content = the ad set format (shared/NAMING.md). The Redavio build adds them; a manual ad must too.
4. **Fix, then re-check.** Pipeline is matched later on utm_campaign, so a wrong UTM loses the credit.

## Output
OK or a list of problems, each with its fix, plus the conversions found.

## Getting the data
1. **Through the Redavio connector** (app.redavio.com/mcp, LinkedIn connected): `paid_linkedin_plan` returns the landing pages the build will use (with UTMs); the Insight Tag and conversions are in Campaign Manager.
2. **Your own data**: a Campaign Manager export with the same columns, or numbers pasted in chat. Nothing in this skill writes to LinkedIn.
