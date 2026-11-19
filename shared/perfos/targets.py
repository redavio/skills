"""Target math: what tCPA / tROAS should be, backed out from the business
(foundations/bi-and-alerts.md). Recommendation only; a human sets it in the platform.
"""
from __future__ import annotations


def pearson(x: list[float], y: list[float]) -> float | None:
    n = len(x)
    if n < 3 or n != len(y):
        return None
    mx, my = sum(x) / n, sum(y) / n
    sx = sum((a - mx) ** 2 for a in x) ** 0.5
    sy = sum((b - my) ** 2 for b in y) ** 0.5
    if not sx or not sy:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def recommend(ltv: float, ltv_to_cac: float, s2_to_won: float, conv_to_s2: float,
              pipeline_per_conversion: float | None = None, media_share_of_cac: float = 1.0,
              weekly_conversions: list[float] | None = None, weekly_s2s: list[float] | None = None,
              min_correlation: float = 0.5) -> dict:
    """Back out the most we can pay at each stage.

    max CAC = LTV / target ratio; paid media's share of it (default all of it).
    max cost per S2 = max media CAC x S2-to-won rate.
    max CPA (the conversion we bid on) = max cost per S2 x conversion-to-S2 rate.
    tROAS = expected pipeline per conversion / max CPA, when conversion values are pipeline-based.
    Before trusting it: in-platform conversions must track S2s week to week.
    """
    max_cac = ltv / ltv_to_cac * media_share_of_cac
    max_cost_per_s2 = max_cac * s2_to_won
    max_cpa = max_cost_per_s2 * conv_to_s2
    out = {
        "max_cac": max_cac, "max_cost_per_s2": max_cost_per_s2, "tcpa": max_cpa,
        "troas": (pipeline_per_conversion / max_cpa) if pipeline_per_conversion and max_cpa else None,
        "why": [
            f"LTV ${ltv:,.0f} / target LTV:CAC {ltv_to_cac:g} = max CAC ${max_cac:,.0f}"
            + (f" (media share {media_share_of_cac:.0%})" if media_share_of_cac != 1 else ""),
            f"x S2 to won {s2_to_won:.0%} = max cost per S2 ${max_cost_per_s2:,.0f}",
            f"x conversion to S2 {conv_to_s2:.1%} = tCPA ${max_cpa:,.0f}",
        ],
    }
    r = pearson(weekly_conversions or [], weekly_s2s or [])
    out["correlation"] = r
    out["trusted"] = r is not None and r >= min_correlation
    if not out["trusted"]:
        out["why"].append("Check first: in-platform conversions don't clearly track S2s "
                          f"(correlation {r:.2f})." if r is not None else
                          "Check first: not enough weekly data to confirm conversions track S2s.")
    return out


def stage_values(acv: float, rate_to_won: dict) -> dict:
    """Value of each funnel stage = ACV x chance a record at that stage becomes a won deal.
    rate_to_won: {stage: probability of reaching closed won from that stage}."""
    return {s: round(acv * p, 2) for s, p in rate_to_won.items()}


def first_target(current: float, goal: float, step_limit: float = 0.15, higher_is_better: bool = False) -> dict:
    """First target sits near current performance, not the goal; tighten in steps no bigger than
    the step limit until it reaches the goal. CPA: lower is better. ROAS: higher is better."""
    steps, t = [], current
    for _ in range(50):
        if (t >= goal) if higher_is_better else (t <= goal):
            break
        t = min(goal, t * (1 + step_limit)) if higher_is_better else max(goal, t * (1 - step_limit))
        steps.append(round(t, 2))
    return {"start": round(current, 2), "goal": goal, "steps": steps}


READY = {"tcpa": 30, "troas": 15}


def ready_for_target(conversions_30d: float, kind: str = "tcpa", platform: str = "google") -> dict:
    """When to add a target to Max Conversions / Max Conversion Value: ~30 conversions in 30 days for
    target CPA, 15 with values for target ROAS (Google's floor). Microsoft: 30 before judging."""
    need = 30 if platform == "microsoft" else READY[kind]
    return {"ready": conversions_30d >= need, "have": conversions_30d, "need": need}
