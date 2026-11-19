"""Tests: sizing, reading and scoring (performance-os actions/tests.md).

A test wins only at 95% confidence on its goal metric. Below that it's learning: logged, not
rolled out. ICE = impact x confidence x ease (1-10 each). Back-test: do high ICE scores win more?
"""
from __future__ import annotations

from math import ceil, erf, sqrt

WIN_CONFIDENCE = 0.95
_Z_TWO_SIDED = {0.80: 1.2816, 0.90: 1.6449, 0.95: 1.9600, 0.99: 2.5758}
_Z_POWER = {0.80: 0.8416, 0.90: 1.2816, 0.95: 1.6449}


def significance(control_conv: float, control_clicks: float, test_conv: float, test_clicks: float,
                 win_confidence: float = WIN_CONFIDENCE) -> dict:
    """Two-proportion z-test on conversion rate, two-sided. Returns rates, lift, confidence, verdict."""
    if min(control_clicks, test_clicks) <= 0:
        return {"lift": None, "confidence": 0.0, "verdict": "inconclusive",
                "reason": "an arm has no clicks"}
    p1, p2 = control_conv / control_clicks, test_conv / test_clicks
    pooled = (control_conv + test_conv) / (control_clicks + test_clicks)
    se = sqrt(pooled * (1 - pooled) * (1 / control_clicks + 1 / test_clicks)) if 0 < pooled < 1 else 0.0
    z = (p2 - p1) / se if se else 0.0
    confidence = erf(abs(z) / sqrt(2))
    lift = (p2 - p1) / p1 if p1 else None
    verdict = "inconclusive" if confidence < win_confidence else ("won" if p2 > p1 else "lost")
    decision = {"won": "Roll out", "lost": "Keep the control",
                "inconclusive": "Log as learning, don't roll out"}[verdict]
    return {"control_rate": p1, "test_rate": p2, "lift": lift, "z": z,
            "confidence": round(confidence, 4), "verdict": verdict, "decision": decision}


def clicks_per_arm(baseline_cvr: float, min_lift: float, confidence: float = 0.95, power: float = 0.80) -> int:
    """Clicks each arm needs to detect a relative lift of min_lift on conversion rate
    (two-sided, normal approximation)."""
    if not 0 < baseline_cvr < 1 or min_lift <= 0:
        raise ValueError("baseline_cvr must be between 0 and 1 and min_lift positive")
    p1, p2 = baseline_cvr, min(baseline_cvr * (1 + min_lift), 0.9999)
    za, zb = _Z_TWO_SIDED[confidence], _Z_POWER[power]
    pbar = (p1 + p2) / 2
    n = (za * sqrt(2 * pbar * (1 - pbar)) + zb * sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2
    return ceil(n)


def read_date_weeks(clicks_needed_per_arm: int, weekly_clicks: float, split: float = 0.5) -> int | None:
    """Whole weeks until each arm has enough clicks, at the current weekly volume and split."""
    per_arm = weekly_clicks * min(split, 1 - split)
    if per_arm <= 0:
        return None
    return max(1, ceil(clicks_needed_per_arm / per_arm))


def ice(impact: float, confidence: float, ease: float) -> float:
    for v in (impact, confidence, ease):
        if not 1 <= v <= 10:
            raise ValueError("ICE scores are 1-10")
    return impact * confidence * ease


def rank(ideas: list[dict]) -> list[dict]:
    """Ideas with impact/confidence/ease, highest ICE first."""
    out = [{**i, "ice": ice(i["impact"], i["confidence"], i["ease"])} for i in ideas]
    return sorted(out, key=lambda i: i["ice"], reverse=True)


def backtest(ideas: list[dict]) -> dict:
    """Win rate for the top third by ICE vs the rest, over finished tests (status won/lost/inconclusive)."""
    done = sorted((i for i in ideas if i.get("status") in ("won", "lost", "inconclusive")),
                  key=lambda i: i["ice"], reverse=True)
    if not done:
        return {"tests": 0}
    cut = max(1, len(done) // 3)
    rate = lambda xs: round(sum(1 for x in xs if x["status"] == "won") / len(xs), 2) if xs else None  # noqa: E731
    return {"tests": len(done), "top_third_win_rate": rate(done[:cut]), "rest_win_rate": rate(done[cut:])}
