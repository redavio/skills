"""Totals and derived metrics. Every number in the system comes from here."""
from __future__ import annotations

from datetime import date
from typing import Callable, Iterable

from .schema import CrmRecord, FactRow

VOLUME = ("impressions", "clicks", "cost", "conversions", "conversion_value",
          "eligible_impressions", "is_impressions", "mqls", "sqls", "s2s", "won", "pipeline", "won_value")


def _div(a, b):
    return a / b if b else None


def derive(t: dict) -> dict:
    """Add rates and cost-per metrics to a dict of volume totals. None when undefined."""
    d = dict(t)
    d["ctr"] = _div(t.get("clicks", 0), t.get("impressions", 0))
    d["cpc"] = _div(t.get("cost", 0), t.get("clicks", 0))
    d["cvr"] = _div(t.get("conversions", 0), t.get("clicks", 0))
    d["cpa"] = _div(t.get("cost", 0), t.get("conversions", 0))
    d["value_per_conversion"] = _div(t.get("conversion_value", 0), t.get("conversions", 0))
    d["roas"] = _div(t.get("conversion_value", 0), t.get("cost", 0))
    d["conv_to_mql"] = _div(t.get("mqls", 0), t.get("conversions", 0))
    d["mql_to_sql"] = _div(t.get("sqls", 0), t.get("mqls", 0))
    d["sql_to_s2"] = _div(t.get("s2s", 0), t.get("sqls", 0))
    d["s2_to_won"] = _div(t.get("won", 0), t.get("s2s", 0))
    d["pipeline_per_s2"] = _div(t.get("pipeline", 0), t.get("s2s", 0))
    d["deal_value"] = _div(t.get("won_value", 0), t.get("won", 0))
    d["cost_per_mql"] = _div(t.get("cost", 0), t.get("mqls", 0))
    d["cost_per_sql"] = _div(t.get("cost", 0), t.get("sqls", 0))
    d["cost_per_s2"] = _div(t.get("cost", 0), t.get("s2s", 0))
    d["cost_per_won"] = _div(t.get("cost", 0), t.get("won", 0))
    d["pipeline_roas"] = _div(t.get("pipeline", 0), t.get("cost", 0))
    d["won_roas"] = _div(t.get("won_value", 0), t.get("cost", 0))
    d["impression_share"] = _div(t.get("is_impressions", 0), t.get("eligible_impressions") or 0)
    return d


def _in(d: date | None, start: date, end: date) -> bool:
    return d is not None and start <= d <= end


def totals(facts: Iterable[FactRow], crm: Iterable[CrmRecord], start: date, end: date,
           key: Callable | None = None) -> dict:
    """Sum facts and CRM stages into groups. Returns {group: derived metrics}.

    Funnel stages are counted by calendar date (when the stage happened), per
    foundations/bi-and-alerts.md. CRM records join to facts on campaign_id after matching.
    key(fact) -> group; CRM records are grouped by the group of their campaign.
    """
    key = key or (lambda f: "total")
    out: dict = {}
    campaign_group: dict = {}
    for f in facts:
        if not (start <= f.date <= end):
            continue
        g = key(f)
        campaign_group[(f.platform, f.campaign_id)] = g
        t = out.setdefault(g, {k: 0.0 for k in VOLUME})
        for k in ("impressions", "clicks", "cost", "conversions", "conversion_value"):
            t[k] += getattr(f, k)
        if f.eligible_impressions is not None:
            # only impressions that have an impression-share figure (search) count toward IS
            t["eligible_impressions"] += f.eligible_impressions
            t["is_impressions"] += f.impressions
    for r in crm:
        g = campaign_group.get((r.platform, r.campaign_id))
        if g is None:
            continue
        t = out[g]
        if _in(r.mql_date, start, end):
            t["mqls"] += 1
        if _in(r.sql_date, start, end):
            t["sqls"] += 1
        if _in(r.s2_date, start, end):
            t["s2s"] += 1
            t["pipeline"] += r.pipeline_value
        if _in(r.won_date, start, end):
            t["won"] += 1
            t["won_value"] += r.won_value
    return {g: derive(t) for g, t in out.items()}


def segment_key(f: FactRow) -> str:
    return f.segment


def platform_key(f: FactRow) -> str:
    return f.platform
