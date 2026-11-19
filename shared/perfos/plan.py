"""Plan: directional funnel forecast, starting budget split and spend scenarios.

A guide for leadership, never a verdict (performance-os foundations/strategy-planning.md).
Search volume and CPC are context: they never add, cut or rank a keyword. Every assumption
carries its source (their data, benchmark, placeholder) and can be overridden.

forecast: searches x share we show for = impressions; x click rate = clicks; x CPC = cost; then
every used conversion point (rate from the previous used point), with CPA and ROAS at each.
split: monthly budget -> Microsoft share off the top -> per platform: Brand at what ~90% of brand
searches cost (never below a floor), PMax test share, Non-brand + Competitor share the rest.
No campaign below the minimum daily budget; the pool pays for raising anything up to it.
scenarios: Base plus each budget increase; each line spends up to its demand ceiling.
"""
from __future__ import annotations

DAYS_PER_MONTH = 30.4
TYPES = ("brand", "nonbrand", "competitor")
PLATFORMS = ("google", "microsoft")

# Starting assumptions. Percentages are whole numbers (10 = 10%). Replace with the account's
# own history as soon as there is any; the source travels with every number.
DEFAULTS: dict[str, tuple[float, str]] = {
    "split:microsoft": (10, "benchmark"),          # Microsoft starts at 10-15% of search budget
    "split:pmax": (10, "benchmark"),               # PMax test share of what's left after Brand
    "split:competitor_of_pool": (50, "placeholder"),
    "split:brand_floor": (30, "placeholder"),      # $/month on Google; Microsoft gets its share
    "split:min_daily": (1, "placeholder"),         # $/day, no campaign below it
    "impression_share:brand": (90, "placeholder"),
    "impression_share:nonbrand": (50, "placeholder"),
    "impression_share:competitor": (30, "placeholder"),
    "ctr:brand": (30, "placeholder"),
    "ctr:nonbrand": (4, "placeholder"),
    "ctr:competitor": (3, "placeholder"),
    "cpc:brand": (2, "placeholder"),
    "cpc:nonbrand": (8, "placeholder"),
    "cpc:competitor": (8, "placeholder"),
    "rate_to_first": (3, "placeholder"),           # click to the first conversion point
    "rate_to_next": (10, "placeholder"),           # each later step
    "scenario:Medium": (20, "benchmark"),
    "scenario:High": (50, "benchmark"),
}


def assumptions(overrides: dict | None = None) -> dict[str, dict]:
    """Defaults overlaid with overrides. Override values may be numbers (source 'their data')
    or {"value": x, "source": "..."}."""
    out = {k: {"value": float(v), "source": s} for k, (v, s) in DEFAULTS.items()}
    for k, v in (overrides or {}).items():
        if isinstance(v, dict):
            out[k] = {"value": float(v["value"]), "source": v.get("source", "their data")}
        else:
            out[k] = {"value": float(v), "source": "their data"}
    return out


def _rate(a: dict, point: str, first: bool) -> tuple[float, str]:
    key = f"rate_to:{point}"
    if key in a:
        return a[key]["value"] / 100, a[key]["source"]
    d = a["rate_to_first" if first else "rate_to_next"]
    return d["value"] / 100, d["source"]


def _mid_cpc(k: dict) -> float | None:
    if not k.get("high_cpc"):
        return None
    return (float(k.get("low_cpc") or 0) + float(k["high_cpc"])) / 2


def _group(keywords, a, google_cpc, points, platform, t):
    kws = [k for k in keywords if k["campaign_type"] == t and k.get("platform", "google") == platform]
    if not kws:
        return None
    searches = float(sum(float(k.get("monthly_searches") or 0) for k in kws))
    own = [c for k in kws if (c := _mid_cpc(k)) is not None]
    borrowed = [google_cpc[k["keyword"]] for k in kws if k["keyword"] in google_cpc]
    if own:
        cpc, cpc_source = sum(own) / len(own), "platform estimate"
    elif borrowed:
        cpc, cpc_source = sum(borrowed) / len(borrowed), "Google estimate"
    else:
        cpc, cpc_source = a[f"cpc:{t}"]["value"], a[f"cpc:{t}"]["source"]
    impressions = searches * a[f"impression_share:{t}"]["value"] / 100
    clicks = impressions * a[f"ctr:{t}"]["value"] / 100
    cost = clicks * cpc
    steps, volume, first = [], clicks, True
    for p in points:
        if not p.get("used", True):
            steps.append({"name": p["name"], "used": False, "volume": None, "cpa": None, "value": 0.0, "roas": None})
            continue
        r, src = _rate(a, p.get("stage") or p["name"], first)
        first = False
        volume *= r
        value = volume * float(p.get("value") or 0)
        steps.append({"name": p["name"], "used": True, "rate": r, "rate_source": src, "volume": volume,
                      "cpa": cost / volume if volume else None, "value": value,
                      "roas": value / cost if cost and p.get("value") else None})
    used = [s for s in steps if s["used"]]
    last_value = used[-1]["value"] if used else 0
    return {"platform": platform, "campaign_type": t, "searches": searches, "impressions": impressions,
            "clicks": clicks, "cpc": cpc, "cpc_source": cpc_source, "cost": cost, "steps": steps,
            "roas": last_value / cost if cost else None}


def forecast(keywords: list[dict], points: list[dict], a: dict) -> dict:
    """keywords: [{keyword, campaign_type, platform, monthly_searches, low_cpc, high_cpc}];
    points: conversion points in funnel order [{name, value, used?, stage?}]; a: assumptions().
    Microsoft gives no CPC for low-traffic terms: Google's is borrowed, and labelled."""
    google_cpc = {k["keyword"]: c for k in keywords
                  if k.get("platform", "google") == "google" and (c := _mid_cpc(k)) is not None}
    present = {k.get("platform", "google") for k in keywords}
    platforms = [p for p in PLATFORMS if p in present] + sorted(present - set(PLATFORMS))
    rows = [r for p in platforms for t in TYPES if (r := _group(keywords, a, google_cpc, points, p, t))]
    total_cost = sum(r["cost"] for r in rows)
    total_steps = []
    for i, p in enumerate(points):
        if not p.get("used", True):
            total_steps.append({"name": p["name"], "used": False, "volume": None, "cpa": None, "value": 0.0, "roas": None})
            continue
        vol = sum(r["steps"][i]["volume"] or 0 for r in rows)
        val = sum(r["steps"][i]["value"] for r in rows)
        total_steps.append({"name": p["name"], "used": True, "volume": vol,
                            "cpa": total_cost / vol if vol else None, "value": val,
                            "roas": val / total_cost if total_cost and p.get("value") else None})
    used = [s for s in total_steps if s["used"]]
    total = {"searches": sum(r["searches"] for r in rows), "clicks": sum(r["clicks"] for r in rows),
             "cost": total_cost, "steps": total_steps,
             "roas": (used[-1]["value"] / total_cost) if used and total_cost else None}
    return {"rows": rows, "total": total}


def split(monthly: float, a: dict, forecast_rows: list[dict], has_competitors: bool,
          daily_overrides: dict | None = None) -> list[dict]:
    """One line per platform and campaign type with monthly and daily budgets.
    daily_overrides: {(platform, campaign_type): daily $} typed over by a person; they win and the
    Non-brand + Competitor pool absorbs the difference."""
    pct = lambda k: a[k]["value"] / 100  # noqa: E731
    shares = {"google": 1 - pct("split:microsoft"), "microsoft": pct("split:microsoft")}
    brand_cost = {(r["platform"], r["campaign_type"]): r["cost"] for r in forecast_rows}
    floor_month = a["split:min_daily"]["value"] * DAYS_PER_MONTH
    lines = []
    for platform in PLATFORMS:
        budget = monthly * shares[platform]
        if budget <= 0:
            continue
        floor = a["split:brand_floor"]["value"] * shares[platform] / shares["google"] if shares["google"] else 0
        brand = min(budget, max(floor, brand_cost.get((platform, "brand"), 0)))
        pmax = (budget - brand) * pct("split:pmax")
        pool = budget - brand - pmax
        competitor = pool * pct("split:competitor_of_pool") if has_competitors else 0
        amounts = {"brand": brand, "nonbrand": pool - competitor, "competitor": competitor, "pmax": pmax}
        amounts = {t: v for t, v in amounts.items() if v > 0}
        raised = {t: max(v, floor_month) for t, v in amounts.items()}
        extra = sum(raised.values()) - sum(amounts.values())
        pool_keys = [t for t in ("nonbrand", "competitor") if raised.get(t, 0) > floor_month]
        while extra > 0.005 and pool_keys:
            share = extra / len(pool_keys)
            for t in list(pool_keys):
                take = min(share, raised[t] - floor_month)
                raised[t] -= take
                extra -= take
                if raised[t] <= floor_month + 0.005:
                    pool_keys.remove(t)
        fixed = {t: v * DAYS_PER_MONTH for (p, t), v in (daily_overrides or {}).items()
                 if p == platform and t in raised}
        diff = sum(fixed.values()) - sum(raised[t] for t in fixed)
        raised.update(fixed)
        pool_keys = [t for t in ("nonbrand", "competitor") if t in raised and t not in fixed]
        while abs(diff) > 0.005 and pool_keys:
            share = diff / len(pool_keys)
            for t in list(pool_keys):
                take = min(share, raised[t] - floor_month) if share > 0 else share
                raised[t] -= take
                diff -= take
                if share > 0 and raised[t] <= floor_month + 0.005:
                    pool_keys.remove(t)
            if share < 0:
                break
        short = sum(raised.values()) > budget + 0.05   # the minimums alone don't fit: say so
        for t, amount in raised.items():
            lines.append({"platform": platform, "campaign_type": t, "monthly": round(amount, 2),
                          "daily": round(amount / DAYS_PER_MONTH, 2),
                          "at_minimum": amount <= floor_month + 0.005, "set_by_you": t in fixed,
                          "minimums_exceed_budget": short})
    return lines


def scenarios(monthly: float, a: dict, fc_rows: list[dict], points: list[dict], has_competitors: bool,
              goals: dict | None = None) -> list[dict]:
    """Base and each 'scenario:<name>' budget increase. goals: {conversion point name: monthly target}.
    PMax has no keyword demand: its spend is shown as not forecast."""
    by_line = {(r["platform"], r["campaign_type"]): r for r in fc_rows}
    named = sorted(((k.split(":", 1)[1], v["value"]) for k, v in a.items() if k.startswith("scenario:")),
                   key=lambda x: x[1])
    out = []
    for name, pct_up in [("Base", 0.0)] + named:
        b = monthly * (1 + pct_up / 100)
        lines = split(b, a, fc_rows, has_competitors)
        spend, not_forecast, capped = 0.0, 0.0, []
        volumes, values = [0.0] * len(points), [0.0] * len(points)
        for line in lines:
            f = by_line.get((line["platform"], line["campaign_type"]))
            if not f or not f["cost"]:
                not_forecast += line["monthly"]
                continue
            share = a[f"impression_share:{line['campaign_type']}"]["value"] / 100
            ceiling = f["cost"] / share if share else f["cost"]
            used = min(line["monthly"], ceiling)
            if line["monthly"] > ceiling:
                capped.append(f"{line['platform']} {line['campaign_type']}")
            spend += used
            for i, s in enumerate(f["steps"]):
                volumes[i] += (s["volume"] or 0) * used / f["cost"]
                values[i] += (s.get("value") or 0) * used / f["cost"]
        steps = []
        for i, p in enumerate(points):
            if not p.get("used", True):
                steps.append({"name": p["name"], "used": False, "volume": None, "cpa": None,
                              "goal": None, "vs_goal": None})
                continue
            goal = (goals or {}).get(p["name"])
            steps.append({"name": p["name"], "used": True, "volume": volumes[i],
                          "cpa": spend / volumes[i] if volumes[i] else None, "value": values[i],
                          "roas": values[i] / spend if spend and values[i] else None,
                          "goal": goal, "vs_goal": (volumes[i] / goal - 1) if goal else None})
        out.append({"scenario": name, "budget": b, "spend_forecast": spend,
                    "spend_not_forecast": not_forecast, "capped_by_demand": capped, "steps": steps})
    return out


def budget_from_goal(pipeline_goal: float, pipeline_per_dollar: float) -> float:
    """Back into spend from the goal: pipeline target / pipeline per dollar (own CRM history)."""
    if pipeline_per_dollar <= 0:
        raise ValueError("pipeline per dollar must be positive")
    return pipeline_goal / pipeline_per_dollar
