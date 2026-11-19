"""Volume gate (actions/recurring-optimization.md).

Clicks-based, so a dud can't burn budget waiting for a conversion that never comes.
Cut when clicks pass the line and the dimension is still below goal:
  0 conv: 3 / goal CVR, 1: 5 / goal CVR, 2: 7 / goal CVR, 3: 9 / goal CVR (locked rule).
For 4+ conversions: the exact one-sided 95% Poisson upper bound, which continues the
same curve (4 -> 9.15). At that line we're 95% sure the true rate is worse than goal.
"""
from __future__ import annotations

from math import exp, factorial

LOCKED = {0: 3.0, 1: 5.0, 2: 7.0, 3: 9.0}


def _poisson_upper(k: int, conf: float = 0.95) -> float:
    """Smallest lambda with P(X <= k) <= 1 - conf (bisection)."""
    def cdf(lam):
        return sum(exp(-lam) * lam ** i / factorial(i) for i in range(k + 1))
    lo, hi = float(k), float(k) + 50.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if cdf(mid) > 1 - conf:
            lo = mid
        else:
            hi = mid
    return hi


def upper_events(conversions: float) -> float:
    k = int(conversions)
    return LOCKED.get(k) or _poisson_upper(k)


def clicks_needed(conversions: float, goal_cvr: float) -> float:
    """Clicks after which `conversions` is 95% surely below goal_cvr."""
    if goal_cvr <= 0:
        raise ValueError("goal conversion rate must be positive")
    return upper_events(conversions) / goal_cvr


def cpa_guard(target_cpa: float | None = None, target_roas: float | None = None,
              value_per_conversion: float | None = None) -> float | None:
    """The cost per conversion that counts as 'too much' for the flag.
    CPA goal: the target CPA. ROAS goal: value per conversion / target ROAS (the CPA the ROAS
    target implies). None when neither can be worked out."""
    if target_cpa:
        return float(target_cpa)
    if target_roas and value_per_conversion:
        return float(value_per_conversion) / float(target_roas)
    return None


def verdict(clicks: float, conversions: float, cost: float, goal_cvr: float,
            target_cpa: float | None = None, conversion_value: float = 0.0,
            target_roas: float | None = None, value_per_conversion: float | None = None) -> dict:
    """One dimension, one window. Returns action + reason.

    Works for all four objectives. Cut always uses the click line on the goal conversion rate.
    Promote needs 3+ conversions, conversion rate at or above goal, and beating the target:
    ROAS >= target_roas when a ROAS target is set, else CPA <= target_cpa when a CPA target is set,
    else conversion rate alone (conversions or conversion value with no target).
    act=True only for cut and promote; flag is view-only.
    """
    cvr = conversions / clicks if clicks else 0.0
    below_goal = cvr < goal_cvr
    need = clicks_needed(conversions, goal_cvr)
    if below_goal and clicks >= need:
        return {"action": "cut", "act": True,
                "reason": f"{conversions:g} conversions on {clicks:g} clicks; past the {need:.0f}-click line for a {goal_cvr:.1%} goal"}
    if conversions >= 3 and not below_goal:
        if target_roas:
            roas = conversion_value / cost if cost else 0.0
            if roas >= target_roas:
                return {"action": "promote", "act": True,
                        "reason": f"{conversions:g} conversions at {roas:.2f} ROAS, beating {target_roas:g} target"}
        elif target_cpa:
            if cost / conversions <= target_cpa:
                return {"action": "promote", "act": True,
                        "reason": f"{conversions:g} conversions at ${cost / conversions:,.0f} CPA, beating ${target_cpa:,.0f} target"}
        else:
            return {"action": "promote", "act": True,
                    "reason": f"{conversions:g} conversions at {cvr:.1%} conversion rate, beating {goal_cvr:.1%} goal"}
    guard = cpa_guard(target_cpa, target_roas, value_per_conversion)
    if conversions == 0 and guard and cost >= 2 * guard:
        return {"action": "flag", "act": False,
                "reason": f"spent ${cost:,.0f} (2x+ the ${guard:,.0f} target cost per conversion) with no conversions; below the click line, watch"}
    return {"action": "watch", "act": False,
            "reason": f"{clicks:g} of {need:.0f} clicks needed to call it"}


def window(daily: list[tuple], goal_cvr: float, max_weeks: int = 13) -> tuple[int, dict]:
    """Smallest whole-week window (7, 14, ...) whose clicks reach the line for its own
    conversion count. daily: [(date, clicks, conversions, cost[, conversion_value])] any order.
    Returns (days, totals). If never reached, returns the longest window (verdict = watch)."""
    rows = sorted(daily, key=lambda r: r[0])
    tot = {}
    for w in range(1, max_weeks + 1):
        days = 7 * w
        part = rows[-days:]
        tot = {"clicks": sum(r[1] for r in part), "conversions": sum(r[2] for r in part),
               "cost": sum(r[3] for r in part),
               "conversion_value": sum((r[4] if len(r) > 4 else 0) for r in part)}
        if tot["clicks"] >= clicks_needed(tot["conversions"], goal_cvr) or len(part) < days:
            return min(days, len(rows)), tot
    return 7 * max_weeks, tot
