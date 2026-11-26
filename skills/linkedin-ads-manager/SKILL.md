---
name: linkedin-ads-manager
description: The LinkedIn Ads manager role for B2B SaaS - one standard, ABM-aware structure of three campaigns (target accounts, ICP reach, engaged), one ad set per ad format with its own budget, built PAUSED through the LinkedIn Marketing API and read back. Covers target-account lists (Clay, G2, CRM), buying-group titles, ICP firmographics, Thought Leader Ads, contact lists, document, video and single image ads, and judging LinkedIn on pipeline at accounts. Use for any LinkedIn Ads, LinkedIn campaign structure, Campaign Manager, Thought Leader Ads or LinkedIn ABM question.
license: MIT
compatibility: Any Agent Skills client with the Redavio connector (https://app.redavio.com/mcp).
metadata:
  role: linkedin-ads-manager
  stage: role
  cadence: Once at setup, then per new campaign
  summary: "The role: the standard 3-campaign LinkedIn structure, built paused and read back, judged on pipeline at accounts."
  needs: The ICP (industries, company sizes, functions, seniority), a target-account list, the landing page, creative
---

# LinkedIn Ads manager

LinkedIn renamed its levels: a **campaign** is what the API calls a campaign group, an **ad set** is the API's campaign, and an ad is a creative. A format (single image, video, document) is fixed per ad set, so every format is its own ad set with its own daily budget.

## The structure (one per client)
| Campaign | Audience | Optimizes for | Ad sets |
|---|---|---|---|
| `linkedin\|aware\|target_accounts\|us\|en` | Target companies (Clay, G2 or the CRM) x buying-group job titles; plus a contact list when you have one | Impressions and reach | Single image, video; Thought Leader when a post is chosen; contact list when one exists |
| `linkedin\|aware\|icp\|us\|en` | ICP firmographics (industry, company size) x job function and seniority; target companies excluded | Impressions and reach | Single image, video; Thought Leader when a post is chosen |
| `linkedin\|engaged\|all\|us\|en` | People who engaged: video viewers, ad and page engagers, site visitors (Insight Tag) | Landing-page clicks | Document, single image |

Settings on every ad set: classic campaigns (not Accelerate), Audience Expansion off, LinkedIn Audience Network off, your own employees excluded, maximum delivery, $10 a day minimum. Ad set names add the format (`...|video`). Landing pages carry `utm_source=linkedin&utm_medium=paid_social&utm_campaign=<campaign>&utm_content=<format>`.

## Principles
- **Judge LinkedIn on pipeline at accounts**: open opportunities and win rate at target accounts it reached in the last 90 days versus ones it didn't. LinkedIn's own 7-day click attribution is shown, never used to judge the channel.
- **Target companies are named in targeting** (looked up on LinkedIn by name); campaign 2 always excludes them, so the two campaigns never bid against each other.
- **Optional pieces are added only when present**: a Thought Leader post adds a Thought Leader ad set to each awareness campaign; a contact list adds a contact-list ad set to the target-accounts campaign. No post or list, no ad set: the build works either way.
- **Everything is built paused (ads as drafts until LinkedIn reviews them), then read back.** A person approves the build; launching is a separate yes.

## How to run it (Redavio connector)
1. Add `https://app.redavio.com/mcp` in Claude (or any MCP client) and sign in.
2. `paid_linkedin_plan`: the plan, the target accounts LinkedIn found, and what blocks a build. If LinkedIn isn't connected it returns a `connect_url`: open it and click Allow with a login that has a role on the ad account.
3. `paid_linkedin_target_accounts`: set the target-account list from company names (it replaces the list; it says which names LinkedIn couldn't find and which matched loosely, so check those).
4. `paid_linkedin_check`: what the build would create (campaigns, ad sets, ads, all paused) and what already exists by name.
5. Build: the operator clicks **Build paused** in the Redavio Client Portal (Build > LinkedIn). It creates everything paused and shows the read-back.

## If something is missing
- No target accounts: ask for the list (company names are enough). Until then campaign 1 can't be built.
- No creative: the images, video and copy come from the client's display creative; the document ad is a 3-page PDF made from the same copy.
- LinkedIn says the app isn't allowed on the ad account: while Redavio's app is on LinkedIn's Development tier, each ad account is added by hand (Developer Portal > app > Products > Advertising API > View Ad Accounts > Add Ad Account). Standard tier removes this step.
- Retargeting audiences and contact-list uploads need LinkedIn's Matched Audiences permission on the app. Until it's granted, the engaged campaign uses company and title targeting and says so.
