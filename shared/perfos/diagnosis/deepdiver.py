"""Deep Diver: which lever drove the gap, as numbers and as one sentence.

Inputs are derived totals (perfos.metrics.totals). Baseline is either the goal (paced) or
the comparison period. Goals for every factor are backed into from the top goal at intake.
"""
from __future__ import annotations

from . import chains as C
from . import mix as M
from . import shapley as S


def diagnose(kpi: str, actual: dict, base: dict, min_volume: dict | None = None,
             chain: dict | None = None, vs: str = "goal") -> dict | None:
    """min_volume: {volume_metric: minimum}, e.g. {"clicks": 60, "sqls": 30}. A factor whose
    denominator volume is below its minimum is kept in the math (shares still sum to 100%)
    but marked low_volume and never named as the main driver."""
    ch = chain or C.CHAINS[kpi]
    res = S.split(ch["factors"], actual, base)
    if res is None:
        return None
    for d in res["drivers"]:
        den = C.DENOMINATOR.get(d["factor"])
        need = (min_volume or {}).get(den) if den else None
        d["low_volume"] = bool(need and actual.get(den, 0) < need)
    res["kpi"] = kpi
    res["higher_is_better"] = ch["higher_is_better"]
    res["gap_pct"] = (res["gap"] / res["base"]) if res["base"] else None
    res["sentence"] = sentence(res, vs)
    return res


def _adverse(res) -> bool:
    return (res["gap"] < 0) if res["higher_is_better"] else (res["gap"] > 0)


def sentence(res: dict, vs: str = "goal") -> str:
    """'Cost per S2 8% over goal: click to conversion rate drove 56%.'"""
    label = C.LABELS.get(res["kpi"], res["kpi"])
    if res["gap_pct"] is None or abs(res["gap_pct"]) < 0.005:
        return f"{label} on {vs}."
    word = ("over" if res["gap"] > 0 else "under") if vs == "goal" else ("up" if res["gap"] > 0 else "down")
    head = f"{label} {abs(res['gap_pct']):.0%} {word} {vs if vs == 'goal' else 'vs prior period'}"
    # the main driver: largest share pushing in the direction of the gap, trusted volume only
    candidates = [d for d in res["drivers"] if d["share"] > 0 and not d["low_volume"]]
    if not candidates:
        return head + ". No single lever stands out with enough volume to call."
    top = max(candidates, key=lambda d: d["share"])
    return f"{head}: {C.LABELS.get(top['factor'], top['factor'])} drove {top['share']:.0%}."


def mix_check(kpi: str, actual_by_seg: dict, base_by_seg: dict) -> dict | None:
    """Mix vs rate for a ratio KPI across segments. Supported: cpa, cost_per_s2, roas,
    pipeline_roas, won_roas."""
    pairs = {"cpa": ("cost", "conversions"), "cost_per_s2": ("cost", "s2s"),
             "roas": ("conversion_value", "cost"), "pipeline_roas": ("pipeline", "cost"),
             "won_roas": ("won_value", "cost")}
    if kpi not in pairs:
        return None
    num, den = pairs[kpi]
    return M.split(actual_by_seg, base_by_seg, num, den)
