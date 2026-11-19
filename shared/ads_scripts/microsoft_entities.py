"""Export Microsoft Ads Search structure as an entity list for the parity check. Read only.
  python3 microsoft_entities.py --out microsoft.json
Same shape as google_entities.py. Status and match type are normalised to Google's words.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _microsoft as MS  # noqa: E402

STATUS = {"active": "enabled", "paused": "paused", "deleted": "removed"}
ap = argparse.ArgumentParser(); ap.add_argument("--account-id"); ap.add_argument("--out")
a = ap.parse_args()
acct = MS.account_id(a.account_id)
cm = MS.service("CampaignManagementService", MS.auth(acct))
out = []
for c in MS.items(cm.GetCampaignsByAccountId(AccountId=acct, CampaignType="Search"), "Campaign"):
    out.append({"type": "campaign", "campaign": c.Name, "name": c.Name, "status": STATUS.get(str(c.Status).lower(), str(c.Status).lower())})
    neg = cm.GetNegativeKeywordsByEntityIds(EntityIds={"long": [c.Id]}, EntityType="Campaign", ParentEntityId=acct)
    for e in MS.items(neg, "EntityNegativeKeywords", "EntityNegativeKeyword"):
        for n in MS.items(e, "NegativeKeywords", "NegativeKeyword"):
            out.append({"type": "negative", "campaign": c.Name, "name": n.Text, "match_type": str(n.MatchType).lower()})
    for g in MS.items(cm.GetAdGroupsByCampaignId(CampaignId=c.Id), "AdGroup"):
        out.append({"type": "ad_group", "campaign": c.Name, "ad_group": g.Name, "name": g.Name,
                    "status": STATUS.get(str(g.Status).lower(), str(g.Status).lower())})
        for k in MS.items(cm.GetKeywordsByAdGroupId(AdGroupId=g.Id), "Keyword"):
            out.append({"type": "keyword", "campaign": c.Name, "ad_group": g.Name, "name": k.Text,
                        "match_type": str(k.MatchType).lower(), "status": STATUS.get(str(k.Status).lower(), str(k.Status).lower())})
        neg = cm.GetNegativeKeywordsByEntityIds(EntityIds={"long": [g.Id]}, EntityType="AdGroup", ParentEntityId=c.Id)
        for e in MS.items(neg, "EntityNegativeKeywords", "EntityNegativeKeyword"):
            for n in MS.items(e, "NegativeKeywords", "NegativeKeyword"):
                out.append({"type": "negative", "campaign": c.Name, "ad_group": g.Name, "name": n.Text,
                            "match_type": str(n.MatchType).lower()})
        for ad in MS.items(cm.GetAdsByAdGroupId(AdGroupId=g.Id, AdTypes={"AdType": ["ResponsiveSearch"]}), "Ad"):
            out.append({"type": "ad", "campaign": c.Name, "ad_group": g.Name, "name": f"rsa:{g.Name}",
                        "status": STATUS.get(str(ad.Status).lower(), str(ad.Status).lower())})
text = json.dumps(out, indent=2)
Path(a.out).write_text(text) if a.out else print(text)
print(f"{len(out)} entities", file=sys.stderr)
