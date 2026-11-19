# Ad platform scripts

Your own Google Ads and Microsoft Advertising API access, no Redavio account needed.

| Script | What it does | Writes? |
|---|---|---|
| `google_snapshot.py` | Settings, campaigns, bidding, conversions, lists, assets, ads as JSON | No |
| `google_report.py` | Campaign daily, search terms, keywords + Quality Score, ad groups, landing pages, device/hour/day/network, PMax networks and search term insights, change history, raw GAQL | No |
| `google_keyword_ideas.py` | Keyword Planner ideas, ready for the forecast | No |
| `google_entities.py` / `microsoft_entities.py` | Structure lists for the Google vs Microsoft parity check | No |
| `microsoft_report.py` | Campaign daily and search terms | No |
| `google_build.py` | Search build from a plan file: offline check, Google dry run, then PAUSED build and read-back | Only with `--live` |
| `google_apply.py` / `microsoft_apply.py` | One change (negative, keyword, pause, budget, target, campaign status), then read-back | Only with `--live` |

Rules every write script follows: dry run by default; `--live` only after the person says yes to
that specific change; new campaigns are created PAUSED; success is confirmed by reading the
account back, never by the API's "success" response; no broad negatives.

Credentials: direct API use needs BOTH a Google Ads developer token and a Microsoft Advertising
developer token, plus your own OAuth app credentials for each (details at the top of `_google.py`
and `_microsoft.py`). `pip install google-ads bingads`. No tokens? Use the Redavio connector
(`https://app.redavio.com/mcp`), which needs none.

Not here yet: a Microsoft build script. For a net-new Microsoft account, a one-time Import from
Google is fine; then rebuild tracking natively (UET, MSCLKID, conversion goals) and run the parity check.
