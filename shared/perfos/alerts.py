"""Daily alerts (performance-os foundations/bi-and-alerts.md). Checks only; alerts never change the account.

Default thresholds (override per account): data missing after 36 hours; tracking break = 3 days of
clicks (20+) with zero conversions after 14 days that had 2+; pacing tolerance 15%.
"""
from __future__ import annotations

import calendar
from datetime import date, datetime

THRESHOLDS = {"data_missing_hours": 36, "tracking_quiet_days": 3, "tracking_before_days": 14,
              "tracking_min_clicks": 20, "tracking_min_conversions_before": 2, "pacing_tolerance_pct": 15}


def data_missing(last_success: dict, now: datetime, hours: float = 36) -> list[str]:
    """Accounts whose last successful data pull is older than `hours` (or never)."""
    return sorted(a for a, t in last_success.items() if t is None or (now - t).total_seconds() > hours * 3600)


def tracking_break(daily: list[tuple], quiet_days: int = 3, min_clicks: float = 20,
                   before_days: int = 14, min_before: float = 2) -> bool:
    """daily: (day, clicks, conversions). True when the last quiet_days had clicks but no conversions
    and the before_days before them had at least min_before conversions."""
    rows = sorted(daily)
    recent, before = rows[-quiet_days:], rows[-(quiet_days + before_days):-quiet_days]
    return (len(recent) == quiet_days and sum(r[1] for r in recent) >= min_clicks
            and sum(r[2] for r in recent) == 0 and sum(r[2] for r in before) >= min_before)


def share_of_period(today: date, start: date | None = None, end: date | None = None) -> float:
    """Share of the period elapsed through yesterday. Defaults to the calendar month of `today`."""
    start = start or today.replace(day=1)
    end = end or today.replace(day=calendar.monthrange(today.year, today.month)[1])
    total = (end - start).days + 1
    elapsed = min(max((today - start).days, 0), total)
    return elapsed / total


def pacing(spend_to_date: float, period_budget: float, today: date, tolerance_pct: float = 15,
           start: date | None = None, end: date | None = None) -> dict:
    """Spend vs the budget's straight-line pace through yesterday. Too early (<3 days) = no call."""
    share = share_of_period(today, start, end)
    s = start or today.replace(day=1)
    if period_budget <= 0 or (today - s).days < 3:
        return {"status": "too_early", "pace": None, "off_pct": None, "message": None}
    pace = period_budget * share
    off = (spend_to_date - pace) / pace * 100
    status = "on_pace" if abs(off) <= tolerance_pct else ("over" if off > 0 else "under")
    msg = None if status == "on_pace" else (
        f"Spend is {abs(off):.0f}% {status} pace (${spend_to_date:,.0f} vs ${pace:,.0f} by now).")
    return {"status": status, "pace": pace, "off_pct": off, "share_elapsed": share, "message": msg}


def goal_pace(actual: float, period_goal: float, share_elapsed: float, higher_is_better: bool = True,
              tolerance_pct: float = 10) -> dict:
    """A volume goal paced to the point in the period (conversions, conversion value, pipeline).
    For rate goals (CPA, ROAS) compare actual to goal directly; don't pace them."""
    paced = period_goal * share_elapsed
    if not paced:
        return {"paced_goal": paced, "vs_goal": None, "status": "too_early"}
    vs = (actual - paced) / paced
    good = vs >= 0 if higher_is_better else vs <= 0
    status = "on_track" if abs(vs) * 100 <= tolerance_pct else ("ahead" if good else "behind")
    return {"paced_goal": paced, "vs_goal": vs, "status": status}
