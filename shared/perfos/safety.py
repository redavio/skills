"""Change safety: which level a change is and what it needs (performance-os foundations/change-log.md).

routine: negatives, keywords, ads, bid or budget moves within the step limit -> the operator approves.
material: moves over the step limit, new campaigns, pausing campaigns -> the client approves too.
destructive: deletes, structure changes, conversion action changes -> client approval and a revert plan.
"""
from __future__ import annotations

DESTRUCTIVE = {"delete", "remove", "restructure", "conversion_action", "change_conversion"}
MATERIAL = {"new_campaign", "pause_campaign", "enable_campaign", "launch"}


def step_limit(raw) -> float | None:
    """'15', '15%' or 0.15 -> 0.15. None if not set."""
    if raw is None or raw == "":
        return None
    try:
        v = float(str(raw).replace("%", "").strip())
    except ValueError:
        return None
    return v / 100 if v > 1 else v


def level(kind: str, move_pct: float | None = None, limit: float | None = None) -> str:
    """kind: what the change does (e.g. negative, keyword, ad, bid, budget, target, new_campaign,
    pause_campaign, delete, restructure, conversion_action). move_pct: size of a bid/budget/target
    move as a fraction. A move that can't be sized against a limit is treated as material."""
    k = (kind or "").lower()
    if k in DESTRUCTIVE:
        return "destructive"
    if k in MATERIAL:
        return "material"
    if move_pct is not None and (limit is None or abs(move_pct) > limit):
        return "material"
    return "routine"


def needs(safety: str) -> list[str]:
    out = ["operator approval"]
    if safety in ("material", "destructive"):
        out.append("client approval (who and when)")
    if safety == "destructive":
        out.append("written revert plan")
    return out


def problem(safety: str, client_approval: str | None, revert_plan: str | None) -> str | None:
    """What's missing before this can be applied, or None."""
    if safety in ("material", "destructive") and not (client_approval or "").strip():
        return "Needs the client's approval: say who approved it and when."
    if safety == "destructive" and not (revert_plan or "").strip():
        return "Needs a written revert plan."
    return None
