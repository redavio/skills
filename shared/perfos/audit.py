"""Audit scoring (performance-os context/checklist.md, context/audit.md).

Headline is always performance vs goals. Setup health is one number: each item scores 2 (pass),
1 (partial) or 0 (fail); Measurement (A1) counts double; shown as a percentage of the maximum.
Items whose channel is off (no PMax, no AI Max, no Microsoft) are not applicable.
"""
from __future__ import annotations

CHECKLIST = {
    "A0": "Intake signed off: goals, targets, budget, conversion values, voice of customer, positioning, messaging",
    "A1": "Measurement: one primary conversion everywhere, every stage sent by click ID with its own value, enhanced conversions, no dead or duplicate conversions",
    "A2": "Settings: Search only, location = presence, auto-apply off, auto assets reviewed, advertiser verified",
    "A3": "Structure: Brand / Non-brand / Competitor, tight themes, geo and language split by campaign",
    "A4": "Targeting: all match types, fencing between campaign types and ad groups, phrase negatives (no broad), login/support handled, customers excluded, observation audiences",
    "A5": "Creative: 1 RSA per ad group, 15 headlines + 4 descriptions from voice of customer, name in 1-2 headlines, no needless pins, extensions maxed",
    "A6": "Landing pages: traffic matches page, one page per theme, CTA leads to the primary conversion, fast, click IDs survive",
    "A7": "Bids and budgets: smart bidding on the right ladder, portfolio per campaign type, Brand budgeted for ~90% impression share",
    "A8": "Delivery: no dead bid adjustments, dead zones excluded only with data",
    "A9": "PMax: own brand excluded, fenced, asset groups mirror Search themes, own video, URL exclusions, same primary conversion",
    "A10": "AI Max: paused copies built, tested as 50/50 experiments (Non-brand, then Brand, then Competitor), URL exclusions, brand fenced",
    "A11": "Microsoft parity: matches Google, tracking built natively, no scheduled imports, own targets",
    "B1": "Budget and impression share: capped winners, capped losers, share lost to rank",
    "B2": "Wasted spend past the volume gate on any lever",
    "B3": "Quality Score, impression-weighted; components read separately",
    "B4": "Experiments running; ranked idea bank",
    "B5": "Change discipline: pace of changes, outside changes flagged, changes graded",
    "B6": "Pacing vs goal",
    "B7": "Ads and assets: no disapprovals, strength good+, no low assets running",
    "B8": "Tracking health: no conversion drop, nothing stopped sending",
}
WEIGHTS = {"A1": 2}
CHANNEL_ITEMS = {"A9": "pmax", "A10": "ai_max", "A11": "microsoft"}
POINTS = {"pass": 2, "partial": 1, "fail": 0}


def score(items: dict, channels_on=None) -> dict:
    """items: {code: 'pass'|'partial'|'fail'|'n/a'}. channels_on: set like {'pmax','ai_max','microsoft'};
    None = all on. Returns setup health % and the failing items in checklist order."""
    total = got = 0
    fails = []
    for code in CHECKLIST:
        status = (items.get(code) or "").lower()
        if not status or status in ("n/a", "na"):
            continue
        if channels_on is not None and CHANNEL_ITEMS.get(code) and CHANNEL_ITEMS[code] not in channels_on:
            continue
        if status not in POINTS:
            raise ValueError(f"{code}: status must be pass, partial, fail or n/a")
        w = WEIGHTS.get(code, 1)
        total += 2 * w
        got += POINTS[status] * w
        if status != "pass":
            fails.append({"code": code, "status": status, "item": CHECKLIST[code]})
    return {"setup_health_pct": round(100 * got / total, 1) if total else None, "points": got,
            "max_points": total, "not_passing": fails,
            "tracking_warning": items.get("A1", "").lower() == "fail"}


def rank_findings(findings: list[dict]) -> list[dict]:
    """findings: {title, impact (1-5, on goals), effort (1-5)}. Highest impact first, then lowest effort."""
    return sorted(findings, key=lambda f: (-f["impact"], f["effort"]))
