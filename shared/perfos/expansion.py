"""Expansion (performance-os actions/expansion.md). Proposes only.

Micro or macro: does it need a new campaign, budget or goal? No = micro (an add inside the
existing structure). Yes = macro: new structure, client sign-off, launched as a test with a read date.
Macro trigger here: an ad group that outgrew its campaign (default 50%+ of the campaign's spend
and 30+ conversions in the window, in a campaign with 2+ ad groups).
"""
from __future__ import annotations

from collections import defaultdict

MICRO_KINDS = {"keyword", "negative", "ad_variant", "audience", "geo", "competitor_in_existing"}


def scope(needs_new_campaign: bool, needs_new_budget: bool, needs_new_goal: bool) -> str:
    return "macro" if (needs_new_campaign or needs_new_budget or needs_new_goal) else "micro"


def outgrown(rows: list[dict], min_share: float = 0.5, min_conversions: float = 30) -> list[dict]:
    """rows: {campaign, ad_group, cost, conversions} summed over the window."""
    by_camp = defaultdict(list)
    for r in rows:
        by_camp[r["campaign"]].append(r)
    out = []
    for camp, groups in by_camp.items():
        total = sum(float(g["cost"]) for g in groups)
        if len(groups) < 2 or total <= 0:
            continue
        for g in groups:
            share = float(g["cost"]) / total
            if share >= min_share and float(g["conversions"]) >= min_conversions:
                out.append({"campaign": camp, "ad_group": g["ad_group"], "share": round(share, 2),
                            "conversions": float(g["conversions"]), "cost": round(float(g["cost"]), 2),
                            "proposal": "own campaign and budget (client sign-off, launch as a test)"})
    return out
