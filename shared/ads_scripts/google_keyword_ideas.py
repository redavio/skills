"""Keyword Planner ideas to CSV (keyword, campaign_type, platform, monthly_searches, low_cpc, high_cpc),
ready for `perfos.cli forecast`. Read only. Volume and CPC are CONTEXT: they never add, cut or rank
a keyword. New brands often show 0; ambiguous seeds pull in junk (check every idea makes sense).

  python3 google_keyword_ideas.py --type nonbrand --seed "budget optimizer" --seed "ppc budget tool" \
      [--geo 2840] [--language 1000] [--limit 30] --out ideas.csv
Geo and language are Google constant IDs (2840 = United States, 1000 = English).
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _google as G  # noqa: E402

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--customer-id"); ap.add_argument("--type", required=True, choices=("brand", "nonbrand", "competitor"))
ap.add_argument("--seed", action="append", required=True)
ap.add_argument("--geo", action="append", default=None); ap.add_argument("--language", default="1000")
ap.add_argument("--limit", type=int, default=30); ap.add_argument("--only-containing-seed", action="store_true",
                                                                    help="keep ideas that contain a seed phrase")
ap.add_argument("--out"); ap.add_argument("--append", action="store_true")
a = ap.parse_args()
cid = G.customer_id(a.customer_id)
g = G.client()
svc = g.get_service("KeywordPlanIdeaService")
req = g.get_type("GenerateKeywordIdeasRequest")
req.customer_id = cid
req.language = f"languageConstants/{a.language}"
for geo in (a.geo or ["2840"]):
    req.geo_target_constants.append(f"geoTargetConstants/{geo}")
req.keyword_plan_network = g.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
req.keyword_seed.keywords.extend(a.seed)
ideas = list(svc.generate_keyword_ideas(request=req))
ideas.sort(key=lambda r: r.keyword_idea_metrics.avg_monthly_searches, reverse=True)
rows = []
for r in ideas:
    if a.only_containing_seed and not any(s.lower() in r.text.lower() for s in a.seed):
        continue
    m = r.keyword_idea_metrics
    rows.append({"keyword": r.text, "campaign_type": a.type, "platform": "google",
                 "monthly_searches": m.avg_monthly_searches, "competition": m.competition.name,
                 "low_cpc": round(m.low_top_of_page_bid_micros / 1e6, 2),
                 "high_cpc": round(m.high_top_of_page_bid_micros / 1e6, 2)})
    if len(rows) >= a.limit:
        break
mode = "a" if a.append and a.out and Path(a.out).exists() else "w"
f = open(a.out, mode, newline="") if a.out else sys.stdout
w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["keyword"])
if mode == "w":
    w.writeheader()
w.writerows(rows)
print(f"{len(rows)} ideas", file=sys.stderr)
