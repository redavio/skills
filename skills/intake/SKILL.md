---
name: intake
description: Run a paid search client or account intake before anything is built or audited - offerings, brand terms, competitors, who to target, where to advertise, voice of customer, positioning and messaging, conversion points with values, goals, budget and the step limit - then get sign-off. Use when starting a new paid search account, client or engagement, onboarding a client, or when someone asks what information is needed before building Google or Microsoft Ads campaigns.
license: MIT
compatibility: Any Agent Skills client. No scripts; the output is a structured intake document.
metadata:
  role: paid-search-lead
  stage: set-up
  summary: The questions to answer and sign off before any build or audit recommendation.
  needs: Someone who knows the business (or its website, positioning doc and analytics)
---

# Intake

Nothing gets built and no audit recommendation is made until the inputs are agreed. The intake
is structured answers (numbers, choices, dates, small tables), not essays; free text only where it
feeds the ad copy (positioning, voice of customer, the copy bank, words to avoid).

## Needs
A person who knows the business. Helpful: their website, positioning or competitor docs, CRM or
analytics access, and a recent sales call or review set for customer quotes.

## If something is missing
Ask in chat, one section at a time, and keep going. Where they don't have the data, agree a
starting value together and mark it **Estimate** (revisit at 90 days with real data). Never fill an
answer in for them; read back what you saved in their words.

## Method
Work the sections in order. Ask what's needed to start first, then offer the rest.

**0. Channels in scope.** Demand capture on Google and Microsoft: Search (option: AI Max),
Performance Max. Everything later only covers the channels that are on.

**1. Targeting (builds the campaigns)**
| Question | Shape | Feeds |
|---|---|---|
| Offerings (products, features, jobs to be done): search terms people use, landing page | table, one row per offering | one Non-brand ad group each |
| Brand terms and misspellings | list | Brand keywords; negatives in Non-brand, Competitor, PMax |
| Competitors: bid on them? name a common word? where they win, where we win, proof, can we name them in ads? | table | Competitor ad groups; common-word names = phrase/exact only. Bidding on a name and naming them in ads are separate decisions |
| Who we target: industries, company sizes, roles (target / exclude) | table | audiences, keyword seeds, negatives |
| Where we advertise: location + language + campaign group | table | geo/language split by campaign |

**2. Messaging (feeds the ads and pages)**
- Voice of customer: real quotes (sales calls, reviews, surveys, tickets), each with its source.
- Problem in the customer's words; alternatives (including doing nothing); what sets us apart (true, provable); proof; 3-5 messaging pillars.
- Approved copy bank (lines used as written). New claims, numbers or competitor statements need their approval.
- Words and claims to avoid; trademark limits.
- If they have positioning or competitor docs, gap-check them against: category, best-fit customer, problem, alternatives, differentiators, value + proof, pillars, words to use and avoid (April Dunford's structure).

**3. Conversions and goals (tracking, bidding, budget, judging)**
- CRM (sends offline conversions back to Google and Microsoft).
- Conversion points: each touch point (form fill, demo, signup, MQL, SQL, opportunity, closed won): primary or secondary (**exactly one primary**, the one bidding optimizes to), where tracked, monthly volume, agreed dollar value, sent to the ad platforms (automatically / by export / website tag / no). Stage value = ACV x chance a record at that stage becomes a deal.
- Measurement tier: 1 = CRM stages flow back automatically with click IDs; 2 = scheduled offline uploads; 3 = no CRM access, optimize to the best on-site conversion. Log the tier with an owner and date to reach Tier 1.
- Goals: period, what's counted (a conversion point, pipeline $ or revenue $), target, plus 30- and 90-day targets. **One objective per campaign: conversions, CPA, conversion value or ROAS.**
- Monthly budget.
- Step limit: the biggest single bid, target or budget move allowed without the client's approval (e.g. 15%).
- Conversion lag (click to conversion) if known.
Not asked here: targets per campaign type and the budget split (forecast-and-budget proposes them).

**Sign-off.** Record what was agreed, who signed off and when, and which values are estimates. Set a 90-day revisit.

## Output
The intake as sections with tables, each answer in their words, estimates marked, then a short
"ready to plan" checklist: what's complete, what's missing, who owns it. Offer to save it as a doc or
sheet if they have Google Docs, Notion or similar connected.

## Getting the data
1. **Redavio connector** (Claude or any MCP client): add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_status` shows which intake sections are done; `paid_search_accounts` lists the accounts.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens): not needed for the intake. Conversion actions already in the account can be read with `google_snapshot.py` (see the audit skill).
3. **Your own data**: their website, docs, CRM exports or a spreadsheet; the intake can live in a Google Sheet or doc with the same sections.
