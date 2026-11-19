"""Report builder (context/reporting.md). Returns data; surfaces render it.

Rows: brand, non-brand (competitor as sub-row), PMax, total, then Google and Bing.
Each cell: value, vs goal (paced), vs comparison period. Driver: one Deep Diver sentence.
"""
from __future__ import annotations

from datetime import date, timedelta

from . import metrics as M
from .diagnosis import deepdiver
from .schema import CrmRecord, FactRow

PAGE1 = ["cost", "conversions", "cpa", "s2s", "cost_per_s2", "pipeline", "pipeline_roas",
         "won_value", "won_roas", "impression_share"]
FUNNEL_VIEW = ["impressions", "clicks", "ctr", "cpc", "conversions", "cvr", "cpa", "mqls",
               "conv_to_mql", "cost_per_mql", "sqls", "mql_to_sql", "cost_per_sql", "s2s",
               "sql_to_s2", "cost_per_s2", "pipeline", "pipeline_roas", "won", "won_value", "won_roas"]
ROWS = [("brand", "Search brand"), ("nonbrand", "Search non-brand"),
        ("competitor", "  incl. competitor"), ("pmax", "PMax"),
        ("unknown", "Unclassified (rename to channel|type|theme|geo|language)"), ("total", "Total"),
        ("google", "  Google"), ("bing", "  Bing")]


def prior_period(start: date, end: date) -> tuple[date, date]:
    n = (end - start).days + 1
    return start - timedelta(days=n), start - timedelta(days=1)


def _group(f: FactRow) -> list[str]:
    # non-brand row includes competitor; competitor also gets its own sub-row
    g = ["total", f.platform, f.segment]
    if f.segment == "competitor":
        g.append("nonbrand")
    return g


def _totals_multi(facts, crm, start, end):
    """Totals for every row key (a fact can count in several rows)."""
    out = {}
    for key in {k for f in facts for k in _group(f)}:
        sub = [f for f in facts if key in _group(f)]
        t = M.totals(sub, crm, start, end)
        out[key] = t.get("total")
    return out


def _pct(a, b):
    return (a - b) / b if (a is not None and b) else None


def build(facts: list[FactRow], crm: list[CrmRecord], start: date, end: date,
          goals: dict | None = None, pace: float = 1.0, compare: tuple[date, date] | None = None,
          driver_kpi: str = "cost_per_s2", columns: list[str] | None = None) -> dict:
    """goals: {row_key: {metric: full-period goal}}. Volume goals are multiplied by pace
    (share of period elapsed); rate goals are not. compare defaults to the prior period."""
    columns = columns or PAGE1
    c_start, c_end = compare or prior_period(start, end)
    cur = _totals_multi(facts, crm, start, end)
    prv = _totals_multi(facts, crm, c_start, c_end)
    rows = []
    for key, label in ROWS:
        a = cur.get(key)
        if a is None:
            continue
        b = prv.get(key) or {}
        g_full = (goals or {}).get(key, {})
        g = {m: (v * pace if m in M.VOLUME else v) for m, v in g_full.items()}
        cells = {m: {"value": a.get(m), "vs_goal": _pct(a.get(m), g.get(m)),
                     "vs_prior": _pct(a.get(m), b.get(m))} for m in columns}
        base, vs = (g, "goal") if driver_kpi in g else (b, "prior")
        driver = None
        if base:
            # factor goals come from intake; fall back to the comparison period's factors
            merged = {**b, **base}
            d = deepdiver.diagnose(driver_kpi, a, merged, vs=vs)
            driver = d["sentence"] if d else None
        rows.append({"key": key, "label": label, "cells": cells, "driver": driver})
    return {"period": (start, end), "compare": (c_start, c_end), "columns": columns, "rows": rows}


def tldr(report: dict) -> list[str]:
    """Plain bullets from the table: the driver sentences of rows that moved."""
    out = []
    for r in report["rows"]:
        if r["driver"] and r["key"] in ("brand", "nonbrand", "pmax", "google", "bing"):
            out.append(f"{r['label'].strip()}: {r['driver']}")
    return out
