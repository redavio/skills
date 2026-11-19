"""Google vs Bing parity check (channels/google-vs-bing.md). Flags drift; never fixes.

Input: entity lists from each platform, as dicts with at least type and name. Budgets and
targets are deliberately not compared: each platform has its own.
"""
from __future__ import annotations

COMPARE_FIELDS = {"campaign": ["status", "geo", "language"],
                  "ad_group": ["status"],
                  "keyword": ["status", "match_type"],
                  "negative": ["match_type"],
                  "ad": ["status", "headlines", "descriptions"],
                  "asset": ["status"]}


def _key(e: dict) -> tuple:
    return (e["type"], e.get("campaign", "").strip().lower(), e.get("ad_group", "").strip().lower(),
            e["name"].strip().lower())


def check(google: list[dict], bing: list[dict]) -> list[dict]:
    g = {_key(e): e for e in google}
    b = {_key(e): e for e in bing}
    drift = []
    for k in sorted(set(g) | set(b)):
        if k not in b:
            drift.append({"issue": "missing_in_bing", "type": k[0], "entity": g[k]["name"], "campaign": k[1]})
        elif k not in g:
            drift.append({"issue": "missing_in_google", "type": k[0], "entity": b[k]["name"], "campaign": k[1]})
        else:
            for field in COMPARE_FIELDS.get(k[0], []):
                gv, bv = g[k].get(field), b[k].get(field)
                if gv != bv:
                    drift.append({"issue": "mismatch", "type": k[0], "entity": g[k]["name"],
                                  "campaign": k[1], "field": field, "google": gv, "bing": bv})
    return drift
