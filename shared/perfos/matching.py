"""Match CRM leads back to ads (foundations/bi-and-alerts.md).

1. Click ID (GCLID, MSCLKID).
2. Fallback: the URL suffix (NAMING.md): campaignid = the campaign ID; utm_campaign = the name slug,
   turned into an ID through campaign_ids when given.
3. Every record logs how it was matched; match rate is a health metric.
"""
from __future__ import annotations

from .schema import CrmRecord


def match(records: list[CrmRecord], click_map: dict[str, tuple[str, str]],
          utm_source_to_platform: dict[str, str] | None = None,
          campaign_ids: dict[str, str] | None = None) -> list[CrmRecord]:
    """click_map: {click_id: (platform, campaign_id)} from the ad platforms' click reports.
    utm_source_to_platform: e.g. {"google": "google", "bing": "bing"}.
    campaign_ids: {utm_campaign slug or campaign name: campaign id}, for records with no campaignid."""
    src = {k.lower(): v for k, v in (utm_source_to_platform or {"google": "google", "bing": "bing",
                                                                 "microsoft": "bing"}).items()}
    for r in records:
        if r.click_id and r.click_id in click_map:
            r.platform, r.campaign_id = click_map[r.click_id]
            r.match_method = "click_id"
        elif (r.campaignid or r.utm_campaign) and r.utm_source and r.utm_source.lower() in src:
            ids = campaign_ids or {}
            r.platform = src[r.utm_source.lower()]
            r.campaign_id = r.campaignid or ids.get(r.utm_campaign) or r.utm_campaign
            r.match_method = "utm"
        else:
            r.match_method = "unmatched"
    return records


def match_rate(records: list[CrmRecord]) -> dict:
    n = len(records)
    counts = {"click_id": 0, "utm": 0, "unmatched": 0}
    for r in records:
        counts[r.match_method or "unmatched"] += 1
    return {**counts, "total": n, "rate": (n - counts["unmatched"]) / n if n else None}


def first_last_touch(r: CrmRecord) -> tuple:
    """First and last touch, always kept alongside the CRM's own model."""
    if not r.touches:
        return None, None
    t = sorted(r.touches, key=lambda x: x.ts)
    return t[0], t[-1]
