"""Export Search structure as an entity list for the parity check (perfos.cli parity). Read only.
  python3 google_entities.py --out google.json
Each entity: {type, campaign, ad_group, name, status, match_type}. Budgets and targets are
deliberately left out: each platform has its own.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _google as G  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--customer-id"); ap.add_argument("--out")
ap.add_argument("--include-paused", action="store_true", default=True)
a = ap.parse_args()
cid = G.customer_id(a.customer_id)
g = G.client()
W = "campaign.status != 'REMOVED' AND campaign.advertising_channel_type = 'SEARCH'"
out = []
for r in G.query(g, cid, f"SELECT campaign.name, campaign.status FROM campaign WHERE {W}"):
    out.append({"type": "campaign", "campaign": r.campaign.name, "name": r.campaign.name, "status": r.campaign.status.name.lower()})
for r in G.query(g, cid, f"SELECT campaign.name, ad_group.name, ad_group.status FROM ad_group WHERE {W} AND ad_group.status != 'REMOVED'"):
    out.append({"type": "ad_group", "campaign": r.campaign.name, "ad_group": r.ad_group.name, "name": r.ad_group.name,
                "status": r.ad_group.status.name.lower()})
for r in G.query(g, cid, "SELECT campaign.name, ad_group.name, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, "
                 f"ad_group_criterion.negative, ad_group_criterion.status FROM ad_group_criterion WHERE {W} "
                 "AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.status != 'REMOVED'"):
    c = r.ad_group_criterion
    out.append({"type": "negative" if c.negative else "keyword", "campaign": r.campaign.name, "ad_group": r.ad_group.name,
                "name": c.keyword.text, "match_type": c.keyword.match_type.name.lower(),
                **({} if c.negative else {"status": c.status.name.lower()})})
for r in G.query(g, cid, "SELECT campaign.name, campaign_criterion.keyword.text, campaign_criterion.keyword.match_type "
                 f"FROM campaign_criterion WHERE {W} AND campaign_criterion.type = 'KEYWORD' AND campaign_criterion.negative = TRUE"):
    out.append({"type": "negative", "campaign": r.campaign.name, "name": r.campaign_criterion.keyword.text,
                "match_type": r.campaign_criterion.keyword.match_type.name.lower()})
for r in G.query(g, cid, "SELECT campaign.name, ad_group.name, ad_group_ad.ad.id, ad_group_ad.status FROM ad_group_ad "
                 f"WHERE {W} AND ad_group_ad.status != 'REMOVED'"):
    out.append({"type": "ad", "campaign": r.campaign.name, "ad_group": r.ad_group.name,
                "name": f"rsa:{r.ad_group.name}", "status": r.ad_group_ad.status.name.lower()})
text = json.dumps(out, indent=2)
Path(a.out).write_text(text) if a.out else print(text)
print(f"{len(out)} entities", file=sys.stderr)
