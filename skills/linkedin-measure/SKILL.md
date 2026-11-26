---
name: linkedin-measure
description: "Measure LinkedIn Ads for B2B SaaS on pipeline at accounts: opportunity rate and pipeline per account at target accounts LinkedIn reached versus ones it didn't over 90 days, with a significance check, instead of LinkedIn's own click attribution. Use for the monthly LinkedIn report, or when someone asks what LinkedIn is worth."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; reading LinkedIn needs the Redavio connector or a Campaign Manager export.
metadata:
  role: linkedin-ads-manager
  stage: review
  cadence: Monthly
  summary: "Pipeline at accounts LinkedIn reached vs ones it didn't: what LinkedIn is worth, monthly."
  needs: "Per account over 90 days: LinkedIn impressions (company report) and CRM opportunities and pipeline"
---

# LinkedIn measurement

LinkedIn is judged on pipeline at the accounts it reached, never on its own 7-day click conversions.

## Needs
- Per target account, last 90 days: impressions from LinkedIn's company report, and opportunities and pipeline from the CRM.

## If something is missing
No company-level impressions: Campaign Manager > Analyze > Company engagement report export. No CRM data: Account Hub or a HubSpot export of opportunities by company.

## Method
1. **Join** LinkedIn's company report to CRM opportunities by company into one CSV: account, impressions, opportunities, pipeline.
2. **Run it**:
   ```
   python3 scripts/run.py perfos linkedin-measure --input accounts.csv
   ```
3. **Read**: opportunity rate and pipeline per account, reached vs not, the lift, and whether it's significant. Reached accounts can be warmer to begin with, so say so; a holdout (linkedin-test) is the clean read.
4. **Report it next to spend**: pipeline per dollar against search and display.

## Output
Reached vs not reached: accounts, with an opportunity, opportunity rate, pipeline, pipeline per account; the lift, its significance, and the caveat. LinkedIn's own conversions only as a footnote.

## Getting the data
1. **Through the Redavio connector** (app.redavio.com/mcp, LinkedIn connected): `paid_linkedin_report` returns spend and delivery; company-level impressions come from Campaign Manager's company report, pipeline from the CRM or Account Hub.
2. **Your own data**: a Campaign Manager export with the same columns, or numbers pasted in chat. Nothing in this skill writes to LinkedIn.
