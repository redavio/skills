"""Budget rebalance: one recommendation per campaign, on the funnel objective.

Objective is pipeline ROAS by default (higher is better), or cost per S2, or any metric in
perfos.metrics.derive. Brand is not budgeted on ROAS (foundations/strategy-planning.md):
pass brand campaigns to brand_check instead.

Rules: adaptive significance window anchored to the
last change, bands sized by gap, volatility dampening, +-max_change cap, increases only for
budget-limited campaigns and sized by recoverable impression share (saturation), the
inefficient-spend cut lane, egregious cuts behind a confidence gate, min/max budget guard,
min-change floor. 
Recommendations only. A human approves; the platform applies and reads back.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, timedelta

from .metrics import derive

DEFAULTS = {
    "objective": "pipeline_roas", "higher_is_better": True,
    "significance_metric": "s2s", "min_events": 10, "stable_min_events": None, "stable_cv": None,
    "base_days": 7, "max_days": 90,
    "bands": [  # (direction, gap_min, gap_max, change)
        ("increase", 0.10, None, 0.20), ("decrease", 0.10, 0.30, 0.10), ("decrease", 0.30, None, 0.20)],
    "max_change": 0.20, "min_change": 0.03,
    "lost_is_budget_threshold": 0.10,
    "cut_lane": True, "cut_min_spend_days": 7.0, "cut_high_mult": 2.0, "cut_low_mult": 0.5,
    "egregious_cut": True, "egregious_spend_pct": 0.25, "cap_break_min_confidence": "medium",
    "min_budget": None, "max_budget": None,
}
_CONF = {"low": 0, "medium": 1, "high": 2}


@dataclass
class Campaign:
    campaign_id: str
    name: str
    segment: str
    current_budget: float
    target: float                              # objective target (e.g. pipeline ROAS 8.0)
    daily: dict = field(default_factory=dict)  # {date: {volume metrics incl. funnel}}
    last_change: date | None = None
    lost_is_budget: float | None = None        # window average, 0..1
    impression_share: float | None = None      # window average, 0..1
    shared_budget: bool = False
    status: str = "enabled"


def adaptive_window(daily_events: dict, period_end: date, base_days: int, min_events: float,
                    max_days: int, earliest_start: date | None = None,
                    stable_min: float | None = None, stable_cv: float | None = None):
    """Expand back from period_end until enough events, never past the last change.
    Returns (days, events, sufficient). """
    acc, window, series = 0.0, 0, []
    for off in range(max(base_days, max_days)):
        d = period_end - timedelta(days=off)
        if earliest_start and d < earliest_start:
            break
        v = float(daily_events.get(d, 0) or 0)
        acc += v
        series.append(v)
        window = off + 1
        if window >= base_days and acc >= min_events:
            return window, acc, True
    ok = acc >= min_events and window >= base_days
    if not ok and stable_min is not None and stable_cv is not None and window >= base_days and acc >= stable_min:
        cv = _cv(series)
        ok = cv is not None and cv <= stable_cv
    return max(window, 1), acc, ok


def _cv(vals):
    if len(vals) < 2:
        return None
    m = sum(vals) / len(vals)
    if not m:
        return None
    return (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5 / abs(m)


def _slope(vals):
    n = len(vals)
    if n < 2:
        return 0.0
    xm, ym = (n - 1) / 2, sum(vals) / n
    den = sum((i - xm) ** 2 for i in range(n))
    return sum((i - xm) * (vals[i] - ym) for i in range(n)) / den if den else 0.0


def signals(daily_vals, target, higher_is_better):
    if not daily_vals or not target:
        return {"confidence": "low", "volatility_adjustment": 0.7, "momentum": 0}
    m = sum(daily_vals) / len(daily_vals)
    if not m:
        return {"confidence": "low", "volatility_adjustment": 0.7, "momentum": 0}
    cv = math.sqrt(sum((v - m) ** 2 for v in daily_vals) / len(daily_vals)) / abs(m)
    s = _slope(daily_vals) / abs(m)
    up = 1 if s > 0.01 else (-1 if s < -0.01 else 0)
    momentum = up if higher_is_better else -up
    gap = abs((m - target) / target)
    n = len(daily_vals)
    conf = "high" if (cv < 0.15 and gap > 0.05 and n >= 5) else ("low" if (cv > 0.35 or n < 3) else "medium")
    return {"confidence": conf, "volatility_adjustment": max(0.5, 1.0 - cv / 0.7), "momentum": momentum}


def _band(bands, direction, gap):
    for d, lo, hi, chg in bands:
        if d == direction and gap >= lo and (hi is None or gap < hi):
            return chg
    return None


def _cut_lane(hib, actual, target, spend, budget, cfg):
    if spend <= 0 or spend < cfg["cut_min_spend_days"] * budget:
        return False
    if actual is None:
        return True
    return actual <= cfg["cut_low_mult"] * target if hib else actual >= cfg["cut_high_mult"] * target


def decide(c: Campaign, period_end: date, config: dict | None = None) -> dict | None:
    cfg = {**DEFAULTS, **(config or {})}
    if c.shared_budget or c.status != "enabled" or not c.current_budget or not c.target:
        return None
    if c.segment == "brand":
        return None  # brand is judged on impression share and holdout, not ROAS
    obj, hib = cfg["objective"], cfg["higher_is_better"]
    floor = c.last_change + timedelta(days=1) if c.last_change else None
    if c.daily:  # never look back past the first day of data (keeps avg daily spend honest)
        first = min(c.daily)
        floor = max(floor, first) if floor else first
    events = {d: m.get(cfg["significance_metric"], 0) for d, m in c.daily.items()}
    days, n_events, ok = adaptive_window(events, period_end, cfg["base_days"], cfg["min_events"],
                                         cfg["max_days"], floor, cfg["stable_min_events"], cfg["stable_cv"])
    if not ok and not cfg["cut_lane"]:
        return None
    start = period_end - timedelta(days=days - 1)
    tot: dict = {}
    for d, m in c.daily.items():
        if start <= d <= period_end:
            for k, v in m.items():
                tot[k] = tot.get(k, 0.0) + v
    t = derive(tot)
    spend = tot.get("cost", 0.0)
    actual = t.get(obj)
    capped = c.lost_is_budget is not None and c.lost_is_budget >= cfg["lost_is_budget_threshold"]

    if actual is None:
        if ok:
            return None
        pct, direction = None, "decrease"
    else:
        pct = (actual - c.target) / c.target
        better = pct > 0 if hib else pct < 0
        direction = "increase" if better else "decrease"
    if not ok and (direction != "decrease" or not _cut_lane(hib, actual, c.target, spend, c.current_budget, cfg)):
        return None
    if not capped:
        if direction == "increase":
            return None
        if not _cut_lane(hib, actual, c.target, spend, c.current_budget, cfg):
            return None
    egregious = cfg["egregious_cut"] and cfg["cut_lane"] and direction == "decrease" and \
        _cut_lane(hib, actual, c.target, spend, c.current_budget, cfg)

    daily_vals = []
    for d in sorted(c.daily):
        if start <= d <= period_end:
            v = derive(c.daily[d]).get(obj)
            if v:
                daily_vals.append(v)
    sig = signals(daily_vals, c.target, hib)

    saturation, egregious_fired, new_budget = None, False, None
    if direction == "increase":
        if not c.impression_share or c.lost_is_budget is None:
            return None  # can't measure recoverable headroom: no increase
        saturation = c.lost_is_budget / c.impression_share
        chg = min(saturation * sig["volatility_adjustment"], cfg["max_change"])
    else:
        # zero return (no CPA, or ROAS of 0) is unambiguous waste: passes the confidence gate
        zero_return = actual is None or (hib and actual == 0)
        conf_ok = zero_return or _CONF[sig["confidence"]] >= _CONF[cfg["cap_break_min_confidence"]]
        if egregious and conf_ok:
            egr = round(cfg["egregious_spend_pct"] * spend / days, 2)
            if 0 < egr < round(c.current_budget * (1 - cfg["max_change"]), 2):
                new_budget, egregious_fired = egr, True
        if not egregious_fired:
            gap = abs(pct) if pct is not None else 2.0
            band = _band(cfg["bands"], "decrease", gap)
            if band is None:
                return None
            chg = min(band * sig["volatility_adjustment"], cfg["max_change"])
    if not egregious_fired:
        if chg < cfg["min_change"]:
            return None
        new_budget = round(c.current_budget * (1 + chg if direction == "increase" else 1 - chg), 2)
    lo, hi = cfg["min_budget"], cfg["max_budget"]
    if (lo is not None and c.current_budget < lo) or (hi is not None and c.current_budget > hi):
        return None
    if hi is not None:
        new_budget = min(new_budget, hi)
    if lo is not None:
        new_budget = max(new_budget, lo)
    change = round(new_budget / c.current_budget - 1, 4)
    if abs(change) < cfg["min_change"] and not egregious_fired:
        return None
    reason = ("egregious_cut" if egregious_fired else "inefficient_spend_cut" if not ok else
              "above_target" if direction == "increase" else "below_target")
    return {
        "campaign_id": c.campaign_id, "campaign": c.name, "segment": c.segment,
        "current_budget": c.current_budget, "recommended_budget": new_budget, "change_pct": change,
        "direction": direction, "objective": obj, "actual": actual, "target": c.target,
        "gap_pct": pct, "reason": reason, "window_days": days, "window_events": n_events,
        "confidence": "low" if not ok else sig["confidence"], "saturation": saturation,
        "status": "proposed",
    }


def brand_check(impression_share: float | None, target_share: float = 0.90) -> dict:
    """Brand is budgeted for coverage, not ROAS."""
    if impression_share is None:
        return {"status": "unknown", "reason": "no impression share data"}
    if impression_share < target_share:
        return {"status": "below", "reason": f"brand impression share {impression_share:.0%} vs {target_share:.0%} target"}
    return {"status": "ok", "reason": f"brand impression share {impression_share:.0%}"}
