# Plan format (google_build.py)

```json
{
  "home_url": "https://www.example.com",
  "locations": [2840],
  "languages": [],
  "protected_terms": ["crm pricing"],
  "shared_negative_lists": [
    {"name": "negatives|brand_terms", "negatives": [["example co", "PHRASE"]]},
    {"name": "negatives|junk", "negatives": [["jobs", "PHRASE"]]}
  ],
  "account_assets": {
    "sitelinks": [{"text": "Pricing", "description1": "Plans for every team", "description2": "Start free", "url": "https://www.example.com/pricing"}],
    "callouts": ["Free 14-Day Trial"],
    "snippet": {"header": "Types", "values": ["Pipeline", "Reporting", "Client Portal"]}
  },
  "campaigns": [{
    "name": "search|nonbrand|agency_crm|us|en",
    "daily_budget": 60,
    "bidding": "max_conversions",
    "portfolio": "portfolio|nonbrand",
    "ai_max": false,
    "url_exclusions": [],
    "negatives": [["crm jobs", "PHRASE"]],
    "shared_negative_lists": ["negatives|brand_terms", "negatives|junk"],
    "ad_groups": [{
      "name": "agency_crm",
      "keywords": [["agency crm", "EXACT"], ["agency crm", "PHRASE"], ["agency crm", "BROAD"]],
      "negatives": [["crm pricing", "EXACT"]],
      "final_url": "https://www.example.com/agencies",
      "headlines": ["... 15 of them, 30 characters max"],
      "descriptions": ["... 4 of them, 90 characters max"],
      "path1": "agencies", "path2": "crm"
    }]
  }]
}
```

- `bidding`: `max_conversions` (CPA or conversions goal) or `max_conversion_value` (ROAS or value goal). Optional `target_cpa` / `target_roas` only for inherited history.
- `locations` / `languages`: Google geo target and language constant IDs. Google has no campaign language setting for Search since Sept 2026; leave `languages` empty unless your API version still accepts it.
- Ad-group `negatives` are the exact-match fencing from negatives-and-fencing.
- `url_exclusions`: path fragments matched with "contains" (e.g. `/careers`), for AI Max copies.
- A full example: `shared/examples/search_plan.json` in the repo.
