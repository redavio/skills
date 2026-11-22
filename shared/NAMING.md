# Naming and UTMs: the one standard

Every skill, script and the Redavio app build and read campaigns with these names and UTMs. Reports
split brand from non-brand, and prospecting from retargeting, by reading the name. Code:
`shared/perfos/naming.py`.

## Campaigns

`channel|segment|theme|geo|language`. Everything lowercase, snake_case inside a slot, `|` with no spaces
and never inside a value.

| Slot | Values |
|---|---|
| channel | `search`, `pmax`, `demandgen`, `youtube`, `audience` (Microsoft Audience ads), `chatgpt` |
| segment | demand capture: `brand`, `nonbrand`, `competitor`; demand creation: `prospecting`, `retargeting` |
| theme | `core` (one campaign, themes as ad groups). A separate theme campaign (`agency_crm`) only when budget, target, geo or goal differ. AI Max copy: add `_aimax` (`core_aimax`) |
| geo | country code (`us`) or a location slug |
| language | first language code (`en`) |

Examples: `search|brand|core|us|en`, `search|nonbrand|core_aimax|us|en`, `pmax|nonbrand|core|us|en`,
`demandgen|retargeting|core|us|en`, `youtube|prospecting|core|us|en`, `audience|prospecting|core|us|en`,
`chatgpt|nonbrand|core|us|en`.

Other objects:
- Bid portfolios: `portfolio|<segment>`, plus `|aimax` for the AI Max test copy (`portfolio|nonbrand|aimax`).
- Shared negative lists: `negatives|<list>` (`negatives|brand_terms`, `negatives|junk`, `negatives|competitors`).
- Ad groups and asset groups: the theme in plain words (`Brand`, `Brand + pricing and sign up`, a
  competitor's name, `Pipeline forecasting`). Display ad groups name their channel set (`all_youtube`,
  `all_channels`, `all_placements`).
- Budgets: `<campaign name> budget`.

Join on IDs, never names, so a rename never breaks history. Older Title Case names (`Search | Non-Brand`)
map to the standard with `naming.standard_name()`; anything it can't map is left alone and flagged.

## UTMs

| Parameter | Value |
|---|---|
| utm_source | `google`, `bing` (Microsoft Advertising), `chatgpt` |
| utm_medium | `cpc` (search, PMax, ChatGPT), `display` (Demand Gen, Microsoft Audience), `video` (YouTube) |
| utm_campaign | the campaign name with `|` replaced by `-` (`search-nonbrand-core-us-en`) |
| utm_content | the ad group ID (Google `{adgroupid}`, Microsoft `{AdGroupId}`); ChatGPT: the ad group slug |
| utm_term | the keyword (`{keyword}` / `{keyword}`), search only |
| campaignid | the campaign ID (`{campaignid}` / `{CampaignId}`): what reports join on |

Where they're set:
- **Search and PMax**: the account-level final URL suffix, with the campaign name slug in a campaign custom
  parameter `cmp`:
  - Google: `utm_source=google&utm_medium=cpc&utm_campaign={_cmp}&utm_content={adgroupid}&utm_term={keyword}&matchtype={matchtype}&device={device}&network={network}&campaignid={campaignid}`
  - Microsoft: `utm_source=bing&utm_medium=cpc&utm_campaign={_cmp}&utm_content={AdGroupId}&utm_term={keyword}&matchtype={MatchType}&device={Device}&network={Network}&campaignid={CampaignId}`
- **Display and video** (Demand Gen, YouTube, Microsoft Audience): a campaign-level final URL suffix,
  because the medium differs: `utm_source=google&utm_medium=display&utm_campaign=<slug>&utm_content={adgroupid}&campaignid={campaignid}`.
- **ChatGPT ads**: no suffix exists, so the UTMs go on each ad's target URL (`naming.with_utms`).

Keep UTMs lowercase. Never put a person's details in a UTM.
