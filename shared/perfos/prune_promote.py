"""Prune or promote checker. Proposes; never applies.

Every dimension is judged the same way against goal, using the volume gate. Output is a
change list for the operator to approve; the platform applies it via API and reads back.
"""
from __future__ import annotations

from collections import defaultdict

from . import gates
from .schema import FactRow

# What each verdict means per level. Anything not listed: "review".
ACTIONS = {
    ("search_term", "cut"): "add as negative (exact)",
    ("search_term", "promote"): "add as keyword (exact)",
    ("keyword", "cut"): "pause keyword",
    ("keyword", "promote"): "graduate to exact / raise bid",
    ("search_theme", "cut"): "remove search theme",
    ("audience", "cut"): "exclude audience",
    ("geo", "cut"): "exclude location",
    ("device", "cut"): "lower device bid adjustment",
    ("hour", "cut"): "exclude hours (dead zone)",
    ("placement", "cut"): "add to placement exclusion list",
    ("network", "cut"): "review network setting",
    ("ad", "cut"): "pause or rewrite ad",
    ("landing_page", "cut"): "test a new page",
    ("day_of_week", "cut"): "exclude days (dead zone)",
    ("match_type", "cut"): "tighten match type",
    ("audience", "promote"): "raise audience bid",
    ("geo", "promote"): "raise location bid",
}


def run(facts: list[FactRow], goals: dict[str, dict], max_weeks: int = 13) -> list[dict]:
    """facts: daily rows at any levels. goals: {segment: {"cvr": x, "cpa": y}} or
    {segment: {"cvr": x, "roas": y, "value_per_conversion": v}} (brand and non-brand have their own). Returns proposals sorted: cuts and promotes first, then flags."""
    series = defaultdict(list)
    meta = {}
    for f in facts:
        k = (f.platform, f.level, f.campaign_id, f.entity_id)
        series[k].append((f.date, f.clicks, f.conversions, f.cost, f.conversion_value))
        meta[k] = f
    out = []
    for k, daily in series.items():
        f = meta[k]
        g = goals.get(f.segment)
        if not g:
            continue  # no goal for this segment: never guess one
        days, tot = gates.window(daily, g["cvr"], max_weeks)
        v = gates.verdict(tot["clicks"], tot["conversions"], tot["cost"], g["cvr"], g.get("cpa"),
                          tot.get("conversion_value", 0.0), g.get("roas"), g.get("value_per_conversion"))
        if days < 7 and v["act"]:
            # 7-day minimum so day-of-week swings cancel; flagrant flags still show
            v = {"action": "watch", "act": False, "reason": "under 7 days of data"}
        if v["action"] == "watch":
            continue
        out.append({
            "platform": f.platform, "level": f.level, "segment": f.segment,
            "campaign": f.campaign_name, "entity": f.entity_name or f.entity_id,
            "verdict": v["action"], "act": v["act"],
            "proposal": ACTIONS.get((f.level, v["action"]), "review") if v["act"] else "view only",
            "reason": v["reason"], "window_days": days, **tot,
        })
    order = {"cut": 0, "promote": 1, "flag": 2}
    return sorted(out, key=lambda p: (order[p["verdict"]], -p["cost"]))
