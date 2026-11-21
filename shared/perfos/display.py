"""Paid display and video math (Google Demand Gen, Microsoft Audience ads).

One scorecard for every display campaign, in this order:
  1. cost to reach   CPM and frequency against a benchmark band (what campaigns bid on)
  2. brand lift      branded search and direct traffic moving with display spend (lagged correlation)
  3. pipeline        pipeline from target accounts (Account Hub, when HubSpot is connected)
Everything else (engaged views, accounts reached, click and view-through conversions) is supporting
detail, never scored.

Also: placement review (placements are judged like search terms, through the volume gate), the
holdout lift test (design and read), reach and retargeting budgets, and creative spec checks.
Standard library only.
"""
from __future__ import annotations

from math import erf, exp, log, sqrt
from statistics import mean, pstdev, stdev

from . import gates

WEEKS_PER_MONTH = 4.33


def _num(v, name: str) -> float:
    try:
        return float(str(v).replace(",", "").replace("$", "")) if v not in (None, "") else 0.0
    except ValueError:
        raise ValueError(f"{name} must be a number, got {v!r}") from None


def _phi(z: float) -> float:
    return 0.5 * (1 + erf(z / sqrt(2)))


# ---------- placement review ----------

ACTIONS = {"cut": "exclude", "promote": "keep", "flag": "hold", "watch": "hold"}


def placement_review(rows: list[dict], goal_cvr: float, target_cpa: float | None = None) -> dict:
    """Placements (or audiences, channels, assets) through the volume gate, like search terms.

    rows: placement, cost, clicks, conversions (the goal conversion, ideally a qualified stage),
    optional impressions and network. Returns every row with its action (exclude / keep / hold),
    share of spend and reason, and the exclusions to propose, biggest spend first.
    """
    if not goal_cvr or goal_cvr <= 0:
        raise ValueError("goal conversion rate must be positive (0.02 = 2%)")
    clean = []
    for r in rows:
        clean.append({"placement": str(r.get("placement") or r.get("name") or "").strip(),
                      "network": r.get("network", ""),
                      "impressions": _num(r.get("impressions"), "impressions"),
                      "clicks": _num(r.get("clicks"), "clicks"),
                      "conversions": _num(r.get("conversions"), "conversions"),
                      "cost": _num(r.get("cost"), "cost")})
    total = sum(r["cost"] for r in clean)
    out = []
    for r in clean:
        v = gates.verdict(r["clicks"], r["conversions"], r["cost"], goal_cvr, target_cpa)
        action = ACTIONS[v["action"]]
        if action == "keep" and r["conversions"] < 3:
            action = "hold"
        out.append(r | {"action": action, "reason": v["reason"],
                        "share_of_spend": round(r["cost"] / total, 4) if total else 0.0,
                        "cpm": round(r["cost"] / r["impressions"] * 1000, 2) if r["impressions"] else None})
    exclude = sorted([r for r in out if r["action"] == "exclude"], key=lambda r: -r["cost"])
    return {"rows": sorted(out, key=lambda r: -r["cost"]), "exclude": exclude,
            "wasted_spend": round(sum(r["cost"] for r in exclude), 2), "goal_cvr": goal_cvr}


# ---------- holdout lift test ----------

def _log_ratios(test: list[float], control: list[float]) -> list[float]:
    return [log(t / c) for t, c in zip(test, control) if t > 0 and c > 0]


def lift_read(test_pre: list[float], test_post: list[float], control_pre: list[float],
              control_post: list[float], min_days: int = 7) -> dict:
    """Read a geo (or audience) holdout: daily metric (branded searches, direct visits, pipeline) in the
    test regions vs the held-back regions, before and during the test. Difference in differences on
    the daily log ratio test/control; 95% two-sided. Verdict: lift / no lift / negative / not enough data."""
    pre, post = _log_ratios(test_pre, control_pre), _log_ratios(test_post, control_post)
    if len(pre) < min_days or len(post) < min_days:
        return {"verdict": "not enough data", "reason": f"need {min_days}+ days in each period with both arms above zero"}
    diff = mean(post) - mean(pre)
    se = sqrt(stdev(pre) ** 2 / len(pre) + stdev(post) ** 2 / len(post))
    z = diff / se if se else 0.0
    confidence = 1 - 2 * (1 - _phi(abs(z)))
    lift = exp(diff) - 1
    if confidence >= 0.95:
        verdict = "lift" if diff > 0 else "negative"
    else:
        verdict = "no lift"
    return {"verdict": verdict, "lift": round(lift, 4), "confidence": round(confidence, 4),
            "pre_days": len(pre), "post_days": len(post),
            "summary": f"Test regions {lift:+.1%} against the holdout at {confidence:.0%} confidence: {verdict}."}


def lift_design(daily_metric: list[float], expected_lift: float, test_days: int = 28,
                pre_days: int | None = None) -> dict:
    """Size a holdout before launch. daily_metric: recent daily values of the lift metric (e.g. branded
    searches). The smallest lift readable at 95% confidence with 80% power, from the metric's day to day
    noise. If the expected lift is smaller, the honest answer is 'not enough to test'."""
    vals = [float(v) for v in daily_metric]
    if len(vals) < 14:
        return {"verdict": "not enough data", "reason": "need 14+ days of the metric to size a test"}
    avg = mean(vals)
    if avg <= 0:
        return {"verdict": "not enough data", "reason": "the metric is zero"}
    cv = pstdev(vals) / avg
    pre = pre_days or len(vals)
    mde = (1.96 + 0.84) * cv * sqrt(2) * sqrt(1 / pre + 1 / test_days)
    ok = expected_lift >= mde
    return {"verdict": "testable" if ok else "not enough to test",
            "min_detectable_lift": round(mde, 4), "expected_lift": expected_lift,
            "read_after_days": test_days if ok else None,
            "note": "Set the holdout at launch: hold back regions (or an audience) that never see the ads."}


# ---------- scorecard ----------

def _pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) < 3 or pstdev(x) == 0 or pstdev(y) == 0:
        return None
    mx, my = mean(x), mean(y)
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return cov / sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))


def _lagged(spend: list[float], metric: list[float], max_lag: int = 3) -> dict:
    best = {"r": None, "lag_weeks": 0}
    for lag in range(max_lag + 1):
        x, y = spend[: len(spend) - lag], metric[lag:]
        r = _pearson(x, y)
        if r is not None and (best["r"] is None or r > best["r"]):
            best = {"r": round(r, 3), "lag_weeks": lag}
    return best


def scorecard(weeks: list[dict], cpm_band: tuple[float, float], pipeline: list[dict] | None = None,
              min_weeks: int = 8, supporting: dict | None = None) -> dict:
    """The one display scorecard. weeks: week, cost, impressions, reach, branded_searches, direct_visits
    (display totals per week). pipeline: [{account, amount}] from Account Hub, or None."""
    cost = sum(_num(w.get("cost"), "cost") for w in weeks)
    imps = sum(_num(w.get("impressions"), "impressions") for w in weeks)
    freqs = [_num(w.get("impressions"), "impressions") / _num(w.get("reach"), "reach")
             for w in weeks if _num(w.get("reach"), "reach")]
    cpm = cost / imps * 1000 if imps else None
    lo, hi = cpm_band
    status = "no data" if cpm is None else "in band" if lo <= cpm <= hi else "above band" if cpm > hi else "below band"
    reach = {"cpm": round(cpm, 2) if cpm is not None else None, "band": [lo, hi], "status": status,
             "weekly_frequency": round(mean(freqs), 2) if freqs else None}

    if len(weeks) < min_weeks:
        brand = {"status": "not enough weeks", "weeks": len(weeks), "needed": min_weeks}
    else:
        spend = [_num(w.get("cost"), "cost") for w in weeks]
        bs = _lagged(spend, [_num(w.get("branded_searches"), "branded_searches") for w in weeks])
        dv = _lagged(spend, [_num(w.get("direct_visits"), "direct_visits") for w in weeks])
        moves = bs["r"] is not None and bs["r"] >= 0.5
        brand = {"r": bs["r"], "lag_weeks": bs["lag_weeks"], "direct_r": dv["r"], "weeks": len(weeks),
                 "status": "moves with spend" if moves else "no clear link",
                 "note": "Correlation, not proof; a holdout (lift-test) proves it."}

    if pipeline is None:
        pipe = {"status": "connect HubSpot", "amount": None}
    else:
        amt = sum(_num(p.get("amount"), "amount") for p in pipeline)
        pipe = {"status": "from target accounts", "amount": amt, "accounts": len(pipeline)}

    return {"scorecard": {"cost_to_reach": reach, "brand_lift": brand, "pipeline": pipe},
            "supporting": supporting or {},
            "note": "Supporting detail is never scored; view-through conversions are always labelled."}


# ---------- budgets ----------

def reach_budget(audience: float, reach_share: float, frequency: float, cpm: float) -> dict:
    """Monthly budget to reach a share of an audience at a frequency: audience x share x frequency x CPM / 1000."""
    for n, v in (("audience", audience), ("reach_share", reach_share), ("frequency", frequency), ("cpm", cpm)):
        if v <= 0:
            raise ValueError(f"{n} must be positive")
    b = audience * reach_share * frequency * cpm / 1000
    return {"monthly_budget": round(b, 2), "impressions": round(audience * reach_share * frequency),
            "people_reached": round(audience * reach_share)}


def retargeting_budget(list_size: float, weekly_frequency: float, cpm: float, total_monthly_spend: float,
                       cap_share: float = 0.01, min_list: int = 100) -> dict:
    """Retargeting is sized from the list, capped at a share of total spend (1% by default, a client setting)."""
    if list_size < min_list:
        return {"monthly_budget": 0, "capped": False,
                "reason": f"list of {list_size:g} is too small to serve (needs {min_list}+)"}
    sized = list_size * weekly_frequency * WEEKS_PER_MONTH * cpm / 1000
    cap = total_monthly_spend * cap_share
    capped = sized > cap
    return {"monthly_budget": round(cap if capped else sized, 2), "sized_from_list": round(sized, 2),
            "cap": round(cap, 2), "capped": capped,
            "reason": (f"capped at {cap_share:.0%} of total spend" if capped else "sized from the list"),
            "keep_if": "its holdout shows lift (lift-test)"}


# ---------- creative specs ----------
# As of 2026-11; check the platform before a big build. ratio = width / height.
SPECS = {
    "google": {
        "image_landscape": {"ratio": 1.91, "min": (600, 314)},
        "image_square": {"ratio": 1.0, "min": (300, 300)},
        "image_portrait": {"ratio": 0.8, "min": (480, 600)},
        "logo": {"ratio": 1.0, "min": (128, 128)},
        "video_horizontal": {"ratio": 16 / 9, "seconds": 10},
        "video_vertical": {"ratio": 9 / 16, "seconds": 10},
        "video_square": {"ratio": 1.0, "seconds": 10},
        "headline": {"chars": 40}, "description": {"chars": 90}, "business_name": {"chars": 25},
    },
    "microsoft": {
        "image_landscape": {"ratio": 1.91, "min": (703, 368)},
        "image_square": {"ratio": 1.0, "min": (300, 300)},
        "logo": {"ratio": 1.0, "min": (128, 128)},
        "video_horizontal": {"ratio": 16 / 9, "seconds": 6},
        "video_vertical": {"ratio": 9 / 16, "seconds": 6},
        "video_square": {"ratio": 1.0, "seconds": 6},
        "headline": {"chars": 30}, "long_headline": {"chars": 90}, "description": {"chars": 90},
        "business_name": {"chars": 25},
    },
}


def creative_check(assets: list[dict], platform: str = "google") -> list[dict]:
    """Each asset against the platform's spec for its format: shape (within 2%), minimum size, length, characters."""
    specs = SPECS.get(platform)
    if specs is None:
        raise ValueError(f"platform must be one of {sorted(SPECS)}")
    out = []
    for a in assets:
        fmt = a.get("format", "")
        s = specs.get(fmt)
        problems = []
        if s is None:
            problems.append(f"{platform} has no {fmt!r} format")
        else:
            if "chars" in s:
                n = len(a.get("text", ""))
                if n > s["chars"]:
                    problems.append(f"{n} characters, limit {s['chars']}")
            if "ratio" in s:
                w, h = float(a.get("width") or 0), float(a.get("height") or 0)
                if not w or not h:
                    problems.append("width and height needed")
                elif abs(w / h - s["ratio"]) / s["ratio"] > 0.02:
                    problems.append(f"shape {w:g}x{h:g} is not {s['ratio']:.2f}:1")
                if w and h and "min" in s and (w < s["min"][0] or h < s["min"][1]):
                    problems.append(f"{w:g}x{h:g} is under the {s['min'][0]}x{s['min'][1]} minimum")
            if "seconds" in s and float(a.get("seconds") or 0) < s["seconds"]:
                problems.append(f"video under {s['seconds']} seconds")
        out.append(a | {"ok": not problems, "problems": problems})
    return out
