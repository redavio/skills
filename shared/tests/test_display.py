"""Paid Display and Video Manager math: placement review, holdout lift test, scorecard, budgets, creative specs.

Planted signals (spec v2, section 11):
- placement review: mobile game apps take ~30% of spend with no qualified leads -> exclude;
  a small placement with too little data -> held by the volume gate.
- lift test: branded search rising only in the test regions -> lift; flat -> no lift;
  underpowered design -> not enough to test.
"""
import json
import random
import subprocess
import sys
from pathlib import Path

import pytest

from perfos import display

SHARED = Path(__file__).resolve().parents[1]
EXAMPLES = SHARED / "examples"


# ---------- placement review ----------

def placements():
    return json.loads((EXAMPLES / "display_placements.json").read_text())


def test_planted_mobile_games_flagged_for_exclusion():
    out = display.placement_review(placements(), goal_cvr=0.02)
    games = next(r for r in out["rows"] if r["placement"] == "mobileapp::2-com.puzzle.match3")
    assert games["action"] == "exclude"
    assert games["share_of_spend"] == pytest.approx(0.30, abs=0.03)
    assert out["exclude"][0]["placement"] == games["placement"]  # biggest waste first


def test_small_placement_held_by_volume_gate():
    out = display.placement_review(placements(), goal_cvr=0.02)
    small = next(r for r in out["rows"] if r["placement"] == "smallblog.example.com")
    assert small["action"] == "hold"


def test_good_placement_kept():
    out = display.placement_review(placements(), goal_cvr=0.02)
    good = next(r for r in out["rows"] if r["placement"] == "youtube.com/channel/b2b-marketing")
    assert good["action"] == "keep"


def test_placement_review_empty_and_bad_input():
    assert display.placement_review([], goal_cvr=0.02)["rows"] == []
    with pytest.raises(ValueError):
        display.placement_review([{"placement": "x", "cost": "abc", "clicks": 1, "conversions": 0}], goal_cvr=0.02)
    with pytest.raises(ValueError):
        display.placement_review(placements(), goal_cvr=0)


# ---------- holdout lift test ----------

def series(n, base, lift=0.0, noise=0.05, seed=1):
    rng = random.Random(seed)
    return [base * (1 + lift) * (1 + rng.gauss(0, noise)) for _ in range(n)]


def test_planted_lift_in_test_regions_reads_as_lift():
    r = display.lift_read(
        test_pre=series(28, 100, seed=1), test_post=series(28, 100, lift=0.15, seed=2),
        control_pre=series(28, 80, seed=3), control_post=series(28, 80, seed=4))
    assert r["verdict"] == "lift"
    assert r["lift"] == pytest.approx(0.15, abs=0.05)
    assert r["confidence"] >= 0.95


def test_flat_reads_as_no_lift():
    r = display.lift_read(
        test_pre=series(28, 100, seed=5), test_post=series(28, 100, seed=6),
        control_pre=series(28, 80, seed=7), control_post=series(28, 80, seed=8))
    assert r["verdict"] == "no lift"


def test_lift_read_too_little_data():
    r = display.lift_read(test_pre=[1, 2], test_post=[1, 2], control_pre=[1, 2], control_post=[1, 2])
    assert r["verdict"] == "not enough data"


def test_underpowered_design_says_not_enough_to_test():
    noisy = series(28, 10, noise=0.6, seed=9)
    d = display.lift_design(daily_metric=noisy, expected_lift=0.05, test_days=14)
    assert d["verdict"] == "not enough to test"
    assert d["min_detectable_lift"] > 0.05


def test_powered_design_is_testable():
    calm = series(28, 100, noise=0.03, seed=10)
    d = display.lift_design(daily_metric=calm, expected_lift=0.10, test_days=28)
    assert d["verdict"] == "testable"
    assert d["read_after_days"] == 28


# ---------- scorecard ----------

def test_scorecard_three_numbers_in_order():
    weeks = [{"week": f"2026-W{w:02d}", "cost": c, "impressions": c * 100, "reach": c * 40,
              "branded_searches": 200 + c * 0.5 + (w % 2), "direct_visits": 500}
             for w, c in enumerate([100, 400, 150, 600, 200, 700, 250, 800, 300, 900], start=30)]
    s = display.scorecard(weeks, cpm_band=(5, 15), pipeline=[{"account": "A", "amount": 50000},
                                                              {"account": "B", "amount": 20000}])
    assert [k for k in s["scorecard"]] == ["cost_to_reach", "brand_lift", "pipeline"]
    assert s["scorecard"]["cost_to_reach"]["cpm"] == pytest.approx(10.0)
    assert s["scorecard"]["cost_to_reach"]["status"] == "in band"
    assert s["scorecard"]["brand_lift"]["r"] > 0.9
    assert s["scorecard"]["pipeline"]["amount"] == 70000
    assert "view_through" not in s["scorecard"]


def test_scorecard_without_crm_says_so():
    s = display.scorecard([{"week": "2026-W40", "cost": 100, "impressions": 10000, "reach": 4000,
                            "branded_searches": 10, "direct_visits": 5}], cpm_band=(5, 15))
    assert s["scorecard"]["pipeline"]["status"] == "connect HubSpot"
    assert s["scorecard"]["brand_lift"]["status"] == "not enough weeks"


# ---------- budgets ----------

def test_reach_budget():
    b = display.reach_budget(audience=200000, reach_share=0.5, frequency=4, cpm=10)
    assert b["monthly_budget"] == pytest.approx(4000.0)


def test_retargeting_capped_at_one_percent_of_total():
    b = display.retargeting_budget(list_size=50000, weekly_frequency=5, cpm=12, total_monthly_spend=100000)
    assert b["monthly_budget"] == pytest.approx(1000.0)
    assert b["capped"] is True


def test_retargeting_sized_from_list_when_under_cap():
    b = display.retargeting_budget(list_size=2000, weekly_frequency=3, cpm=10, total_monthly_spend=100000)
    assert b["monthly_budget"] == pytest.approx(2000 * 3 * 4.33 * 10 / 1000, rel=0.01)
    assert b["capped"] is False


def test_retargeting_list_too_small():
    b = display.retargeting_budget(list_size=50, weekly_frequency=3, cpm=10, total_monthly_spend=100000)
    assert b["monthly_budget"] == 0 and "too small" in b["reason"]


# ---------- creative specs ----------

def test_creative_check_every_format():
    assets = [
        {"format": "image_landscape", "width": 1200, "height": 628},
        {"format": "image_square", "width": 1200, "height": 1200},
        {"format": "image_portrait", "width": 960, "height": 1200},
        {"format": "logo", "width": 1200, "height": 1200},
        {"format": "video_horizontal", "width": 1920, "height": 1080, "seconds": 20},
        {"format": "video_vertical", "width": 1080, "height": 1920, "seconds": 20},
        {"format": "video_square", "width": 1080, "height": 1080, "seconds": 20},
        {"format": "headline", "text": "Budgets that move themselves"},
        {"format": "description", "text": "Daily budget recommendations for Google and Microsoft Ads. You approve every change."},
    ]
    out = display.creative_check(assets, platform="google")
    assert all(a["ok"] for a in out), [a for a in out if not a["ok"]]


def test_creative_check_catches_wrong_shape_and_long_text():
    out = display.creative_check([
        {"format": "video_vertical", "width": 1920, "height": 1080, "seconds": 20},
        {"format": "headline", "text": "x" * 41},
        {"format": "image_landscape", "width": 300, "height": 157},
    ], platform="google")
    assert [a["ok"] for a in out] == [False, False, False]


# ---------- CLI ----------

def test_cli_placements_and_lift_design():
    run = lambda *a: json.loads(subprocess.run([sys.executable, "-m", "perfos.cli", *a], cwd=SHARED,
                                               capture_output=True, text=True, check=True).stdout)
    out = run("placements", "--input", str(EXAMPLES / "display_placements.json"), "--goal-cvr", "0.02")
    assert out["exclude"][0]["placement"] == "mobileapp::2-com.puzzle.match3"
    b = run("reach-budget", "--audience", "200000", "--reach-share", "0.5", "--frequency", "4", "--cpm", "10")
    assert b["monthly_budget"] == 4000
