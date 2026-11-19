from datetime import date, timedelta

import pytest

from perfos import gates


def test_locked_rule_of_three():
    assert gates.clicks_needed(0, 0.05) == pytest.approx(60)
    assert gates.clicks_needed(1, 0.05) == pytest.approx(100)
    assert gates.clicks_needed(2, 0.05) == pytest.approx(140)
    assert gates.clicks_needed(3, 0.05) == pytest.approx(180)


def test_curve_keeps_rising_past_three():
    assert gates.upper_events(4) == pytest.approx(9.15, abs=0.01)
    assert gates.upper_events(10) > gates.upper_events(4)


def test_verdicts():
    assert gates.verdict(60, 0, 300, 0.05, 100)["action"] == "cut"
    assert gates.verdict(59, 0, 100, 0.05, 100)["action"] == "watch"
    assert gates.verdict(30, 0, 250, 0.05, 100)["action"] == "flag"
    assert gates.verdict(40, 3, 240, 0.05, 100)["action"] == "promote"


def test_window_is_whole_weeks():
    d0 = date(2026, 10, 1)
    daily = [(d0 + timedelta(days=i), 5, 0, 10) for i in range(30)]  # 5 clicks a day, no conv
    days, tot = gates.window(daily, 0.05)
    assert days % 7 == 0 and tot["clicks"] >= 60
