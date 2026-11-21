"""Pull ChatGPT ads data with your own Ads API key. Read only (GET); nothing here can change the account.

  export OPENAI_ADS_API_KEY=...            Ads Manager > Settings > General > API Keys
  python3 chatgpt_report.py account        check the key: account ID, name, status
  python3 chatgpt_report.py campaigns      campaigns with status, objective and budget
  python3 chatgpt_report.py ad_groups      every ad group with its context hints
  python3 chatgpt_report.py insights --days 56 [--clusters clusters.json] --out insights.csv

insights writes one row per ad group per week (Monday start) in the columns `perfos chatgpt-weekly`
reads: week, campaign, ad_group, cluster, impressions, clicks, spend, conversions. Spend is in account
currency. Attribution is OpenAI's default (30-day click, 1-day view) unless you pass --click-days and
--view-days. clusters.json maps ad group name -> topic cluster (chatgpt-bulk writes it); without it the
cluster column is blank and the skill asks for it.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _chatgpt as C  # noqa: E402

FIELDS = ["week", "campaign", "ad_group", "cluster", "impressions", "clicks", "spend", "conversions"]


def ad_groups(c):
    for camp in c.get_all("/campaigns"):
        for g in c.get_all("/ad_groups", {"campaign_id": camp["id"]}):
            yield camp, g


def insights(c, days, clusters, click_days, view_days):
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    rng = json.dumps({"type": "date_range", "since": start.isoformat(), "until": end.isoformat()})
    weeks: dict[tuple, dict] = {}
    for camp, g in ad_groups(c):
        params = {"time_ranges[]": rng, "time_granularity": "daily", "limit": 2000,
                  "fields[]": ["impressions", "clicks", "spend", "conversions"],
                  "attribution_window_days": click_days, "view_through_attribution_window_days": view_days}
        rows = c.get_all(f"/ad_groups/{g['id']}/insights", params, limit=2000)
        for r in C.insight_rows(rows, camp.get("name", ""), g.get("name", ""), clusters.get(g.get("name", ""), "")):
            d = date.fromisoformat(str(r["week"])[:10])
            wk = (d - timedelta(days=d.weekday())).isoformat()
            k = (wk, r["campaign"], r["ad_group"])
            acc = weeks.setdefault(k, {**r, "week": wk, "impressions": 0, "clicks": 0, "spend": 0.0, "conversions": 0})
            for m in ("impressions", "clicks", "spend", "conversions"):
                acc[m] += float(r.get(m) or 0)
    return [weeks[k] for k in sorted(weeks)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["account", "campaigns", "ad_groups", "insights"])
    ap.add_argument("--days", type=int, default=56)
    ap.add_argument("--clusters", help="JSON {ad group name: cluster}")
    ap.add_argument("--click-days", type=int, choices=[7, 14, 30], default=30)
    ap.add_argument("--view-days", type=int, choices=[0, 1], default=1)
    ap.add_argument("--out", help="CSV path (insights); default prints")
    a = ap.parse_args(argv)
    c = C.Client()
    try:
        if a.what == "account":
            acct = c.get("/ad_account")
            print(json.dumps({k: acct.get(k) for k in ("id", "name", "status", "currency", "timezone")}, indent=2))
        elif a.what == "campaigns":
            print(json.dumps([{k: x.get(k) for k in ("id", "name", "status", "bidding_type", "budget")}
                              for x in c.get_all("/campaigns")], indent=2))
        elif a.what == "ad_groups":
            print(json.dumps([{"campaign": camp.get("name"), "id": g.get("id"), "name": g.get("name"),
                               "status": g.get("status"), "context_hints": g.get("context_hints", [])}
                              for camp, g in ad_groups(c)], indent=2))
        else:
            clusters = json.loads(Path(a.clusters).read_text()) if a.clusters else {}
            rows = insights(c, a.days, clusters, a.click_days, a.view_days)
            f = open(a.out, "w", newline="") if a.out else sys.stdout
            w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
            if a.out:
                f.close()
                print(f"{len(rows)} ad group weeks -> {a.out}", file=sys.stderr)
    except RuntimeError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
