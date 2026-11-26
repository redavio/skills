---
name: linkedin-target-accounts
description: "Build and check the LinkedIn target-account list for B2B SaaS ABM: company names from Clay, G2, Account Hub, HubSpot or a CRM, cleaned (legal suffixes, duplicates), matched on LinkedIn by name, with misses and loose matches flagged for a person to check. Use when setting up or refreshing LinkedIn target accounts or ABM targeting."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; reading LinkedIn needs the Redavio connector or a Campaign Manager export.
metadata:
  role: linkedin-ads-manager
  stage: set-up
  cadence: Once at setup, then monthly
  summary: "Your target companies cleaned, matched on LinkedIn by name, and every miss or loose match flagged."
  needs: "Target company names (Clay, G2, Account Hub, HubSpot or the CRM)"
---

# LinkedIn target accounts

The target-accounts campaign is only as good as the list. Names are cleaned, matched on LinkedIn, and anything doubtful goes to a person.

## Needs
- Company names, one per line or a CSV column (Clay, G2 intent, Account Hub's top accounts, HubSpot target accounts or a CRM view).

## If something is missing
No list: ask which source holds the target accounts; Account Hub's highest-scoring accounts are a good start. Fewer than 100 companies: say the audience will be small and point to linkedin-plan.

## Method
1. **Clean the names**:
   ```
   python3 scripts/run.py perfos linkedin-accounts --input accounts.csv
   ```
   Legal suffixes and duplicates are removed; show what changed.
2. **Match on LinkedIn**: `paid_linkedin_target_accounts` with the cleaned names (it replaces the list; ask first). It looks each company up on LinkedIn.
3. **Check the matches**: `paid_linkedin_plan` returns each company's match; run `perfos linkedin-accounts --matches matches.json` to list misses and loose matches (under 85% similar). A person confirms or fixes each.
4. **Refresh monthly** from the same source, so closed-won and disqualified companies drop out.

## Output
Counts (found / total), the companies LinkedIn didn't find, loose matches to check side by side, and what was cleaned. The list is saved in Redavio only; nothing changes on LinkedIn until a build.

## Getting the data
1. **Through the Redavio connector** (app.redavio.com/mcp, LinkedIn connected): `paid_linkedin_target_accounts` sets and matches the list; `paid_linkedin_plan` returns each company's match.
2. **Your own data**: a Campaign Manager export with the same columns, or numbers pasted in chat. Nothing in this skill writes to LinkedIn.
