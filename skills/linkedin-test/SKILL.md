---
name: linkedin-test
description: "Design a LinkedIn holdout test for B2B SaaS at the account level: split the target accounts into a test group and a holdout excluded from every LinkedIn campaign, repeatably, then read opportunity rate and pipeline in both groups after 8-12 weeks. Use when someone asks whether LinkedIn really drives pipeline, or wants proof before raising LinkedIn's budget."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; reading LinkedIn needs the Redavio connector or a Campaign Manager export.
metadata:
  role: linkedin-ads-manager
  stage: run
  cadence: Once per quarter
  summary: "A repeatable account-level holdout, then pipeline in both groups: does LinkedIn add pipeline?"
  needs: "The target-account list (100+ companies for a readable result); CRM opportunities and pipeline per account after the test"
---

# LinkedIn holdout test

The clean answer to "is LinkedIn working": hold back half the target accounts, then compare pipeline.

## Needs
- The target-account list (100+ companies; fewer and the result won't read).
- After 8-12 weeks: opportunities and pipeline per account from the CRM.

## If something is missing
Under 100 accounts: say the test can't separate a real lift from noise; use linkedin-measure's everyday read instead.

## Method
1. **Split**:
   ```
   python3 scripts/run.py perfos linkedin-holdout --input accounts.csv [--holdout-share 0.5]
   ```
   The same list always gives the same split.
2. **Exclude the holdout**: add the holdout companies as an exclusion on every LinkedIn campaign (a person approves the change). Don't change anything else for the test's length.
3. **Wait 8-12 weeks** (B2B pipeline is slow).
4. **Read**: put both groups in one CSV (account, impressions, opportunities, pipeline; holdout accounts with 0 impressions) and run `perfos linkedin-measure`. The significance line says whether the difference is real.

## Output
The split (test and holdout lists with counts) and the exclusion to add; at the end, opportunity rate and pipeline per account in each group, the lift and whether it's significant.

## Getting the data
1. **Through the Redavio connector** (app.redavio.com/mcp, LinkedIn connected): `paid_linkedin_plan` returns the target-account list; the exclusion is added in Campaign Manager or the next build after a person's yes.
2. **Your own data**: a Campaign Manager export with the same columns, or numbers pasted in chat. Nothing in this skill writes to LinkedIn.
