---
name: linkedin-build
description: "Build the standard LinkedIn Ads structure for B2B SaaS through the LinkedIn Marketing API: three campaigns (target accounts, ICP reach, engaged), one ad set per format with its own daily budget, Audience Expansion and the Audience Network off, own employees excluded; Check first, then Build paused and read back. Use when someone asks to build, rebuild or check LinkedIn campaigns."
license: MIT
compatibility: Any Agent Skills client. Scripts need Python 3.10+, standard library only; reading LinkedIn needs the Redavio connector or a Campaign Manager export.
metadata:
  role: linkedin-ads-manager
  stage: set-up
  cadence: Once at setup, then per new campaign
  summary: "The 3-campaign structure: Check, then Build paused, then read back from LinkedIn."
  needs: "LinkedIn connected, target accounts, creative and a landing page"
---

# LinkedIn build

One structure per client, built the same way every time: Check shows what will be made, a person clicks Build paused, and LinkedIn is read back.

## Needs
- LinkedIn connected with a login that has a role on the ad account.
- Target accounts (linkedin-target-accounts), creative (linkedin-ad-copy) and a landing page.

## If something is missing
Not connected: paid_linkedin_plan returns a connect link. LinkedIn says the app isn't allowed on the ad account: while the app is on LinkedIn's Development tier, the account is added under the developer app's Products > Advertising API > View Ad Accounts.

## Method
1. **Plan**: `paid_linkedin_plan` shows the campaigns, ad sets, budgets, resolved targeting and anything blocking.
2. **Check**: `paid_linkedin_check` lists what would be created and what already exists by name. Nothing is saved.
3. **Build**: a person clicks **Build paused** in the Client Portal (Build > LinkedIn). Campaigns and ad sets are created paused and ads as drafts (LinkedIn reviews ads before they can be paused or run).
4. **Read back**: the build returns every campaign and ad set with its status and ad count; anything missing is listed. Running it again only adds what's missing.
5. **Launch is separate**: a payment method on the ad account and the person's yes.

## Output
What was created and skipped, then the read-back table: every campaign and ad set, its status, and its ads.

## Getting the data
1. **Through the Redavio connector** (app.redavio.com/mcp, LinkedIn connected): `paid_linkedin_plan`, `paid_linkedin_check`; the build itself is the Client Portal's Build paused button.
2. **Your own data**: a Campaign Manager export with the same columns, or numbers pasted in chat. Nothing in this skill writes to LinkedIn.
