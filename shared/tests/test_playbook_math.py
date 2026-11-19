import json
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from perfos import alerts, audit, experiments, expansion, fencing, gates, limits, plan, safety, targets

SHARED = Path(__file__).resolve().parents[1]


# ---- volume gate, all four objectives ----
def test_roas_goal_promotes_on_roas_not_cpa():
    v = gates.verdict(60, 4, 400, 0.05, target_cpa=None, conversion_value=2000, target_roas=4)
    assert v["action"] == "promote"
    v = gates.verdict(60, 4, 800, 0.05, target_cpa=None, conversion_value=2000, target_roas=4)
    assert v["action"] == "watch"


def test_roas_flag_uses_implied_cpa():
    # value per conversion 400 at 4x ROAS -> implied CPA 100; 2x = 200
    assert gates.verdict(20, 0, 210, 0.05, None, 0, 4, 400)["action"] == "flag"
    assert gates.cpa_guard(None, 4, 400) == pytest.approx(100)


def test_conversions_goal_without_target_promotes_on_rate():
    assert gates.verdict(50, 4, 500, 0.05)["action"] == "promote"


# ---- plan ----
def _kw():
    return [{"keyword": "acme", "campaign_type": "brand", "platform": "google", "monthly_searches": 1000, "low_cpc": 1, "high_cpc": 3},
            {"keyword": "crm software", "campaign_type": "nonbrand", "platform": "google", "monthly_searches": 5000, "low_cpc": 6, "high_cpc": 14},
            {"keyword": "crm software", "campaign_type": "nonbrand", "platform": "microsoft", "monthly_searches": 600}]


def test_forecast_funnel_and_borrowed_cpc():
    a = plan.assumptions()
    f = plan.forecast(_kw(), [{"name": "Demo", "value": 100}, {"name": "S2", "value": 2000}], a)
    ms = next(r for r in f["rows"] if r["platform"] == "microsoft")
    assert ms["cpc_source"] == "Google estimate" and ms["cpc"] == pytest.approx(10)
    nb = next(r for r in f["rows"] if r["platform"] == "google" and r["campaign_type"] == "nonbrand")
    assert nb["clicks"] == pytest.approx(5000 * 0.5 * 0.04)
    assert nb["steps"][0]["volume"] == pytest.approx(nb["clicks"] * 0.03)
    assert nb["steps"][1]["volume"] == pytest.approx(nb["clicks"] * 0.03 * 0.10)


def test_split_respects_minimum_and_sums_to_budget():
    a = plan.assumptions({"split:min_daily": 10})
    f = plan.forecast(_kw(), [{"name": "Demo", "value": 100}], a)
    lines = plan.split(30000, a, f["rows"], has_competitors=True)
    assert sum(l["monthly"] for l in lines) == pytest.approx(30000, abs=0.05)
    assert all(l["daily"] >= 10 - 0.01 for l in lines)
    small = plan.split(3000, a, f["rows"], has_competitors=True)
    assert any(l["minimums_exceed_budget"] for l in small if l["platform"] == "microsoft")
    assert {l["platform"] for l in lines} == {"google", "microsoft"}


def test_daily_override_wins_and_pool_absorbs():
    a = plan.assumptions()
    f = plan.forecast(_kw(), [{"name": "Demo", "value": 100}], a)
    lines = plan.split(5000, a, f["rows"], True, {("google", "pmax"): 5})
    pm = next(l for l in lines if l["platform"] == "google" and l["campaign_type"] == "pmax")
    assert pm["daily"] == pytest.approx(5) and pm["set_by_you"]
    assert sum(l["monthly"] for l in lines) == pytest.approx(5000, abs=0.05)


def test_scenarios_cap_by_demand():
    a = plan.assumptions()
    f = plan.forecast(_kw(), [{"name": "Demo", "value": 100}], a)
    s = plan.scenarios(100000, a, f["rows"], [{"name": "Demo", "value": 100}], True, {"Demo": 50})
    assert [x["scenario"] for x in s] == ["Base", "Medium", "High"]
    assert s[0]["capped_by_demand"]


# ---- tests ----
def test_significance_and_size():
    r = experiments.significance(40, 1000, 70, 1000)
    assert r["verdict"] == "won" and r["confidence"] >= 0.95
    assert experiments.significance(40, 1000, 44, 1000)["verdict"] == "inconclusive"
    n = experiments.clicks_per_arm(0.05, 0.2)
    assert 7000 < n < 9000
    assert experiments.read_date_weeks(n, 2000) == pytest.approx(n / 1000, abs=1)


def test_ice_rank_and_backtest():
    ideas = [{"hypothesis": "a", "impact": 9, "confidence": 8, "ease": 7, "status": "won"},
             {"hypothesis": "b", "impact": 2, "confidence": 2, "ease": 2, "status": "lost"},
             {"hypothesis": "c", "impact": 5, "confidence": 5, "ease": 5, "status": "inconclusive"}]
    r = experiments.rank(ideas)
    assert r[0]["hypothesis"] == "a"
    assert experiments.backtest(r)["top_third_win_rate"] == 1.0


# ---- safety ----
def test_safety_levels():
    assert safety.level("negative") == "routine"
    assert safety.level("budget", 0.10, safety.step_limit("15%")) == "routine"
    assert safety.level("budget", 0.30, 0.15) == "material"
    assert safety.level("budget", 0.10, None) == "material"
    assert safety.level("conversion_action") == "destructive"
    assert safety.problem("destructive", "client, 11/1", None) == "Needs a written revert plan."


# ---- alerts ----
def test_pacing_and_goal_pace():
    p = alerts.pacing(2000, 3000, date(2026, 11, 16), 15)
    assert p["status"] == "over"
    assert alerts.pacing(100, 3000, date(2026, 11, 2))["status"] == "too_early"
    g = alerts.goal_pace(40, 100, 0.5)
    assert g["status"] == "behind"


def test_tracking_break():
    d0 = date(2026, 11, 1)
    rows = [(d0 + timedelta(days=i), 20, 1 if i < 14 else 0) for i in range(17)]
    assert alerts.tracking_break(rows)
    assert alerts.data_missing({"g": datetime(2026, 11, 1)}, datetime(2026, 11, 3), 36) == ["g"]


# ---- expansion, limits, fencing, audit, targets ----
def test_outgrown():
    rows = [{"campaign": "c", "ad_group": "big", "cost": 900, "conversions": 40},
            {"campaign": "c", "ad_group": "small", "cost": 100, "conversions": 2}]
    assert expansion.outgrown(rows)[0]["ad_group"] == "big"


def test_rsa_limits():
    errs = limits.check_rsa(["x" * 31] + [f"h{i}" for i in range(14)], ["d1", "d2", "d3", "d4"])
    assert any("over 30" in e for e in errs)
    assert limits.check_rsa([f"h{i}" for i in range(15)], ["a", "b", "c", "d"], "p", "q") == []
    assert limits.check_pmax(["h"] * 3, ["l"], ["x" * 61, "y" * 61]) == ["needs one description of 60 characters or fewer"]


def test_fencing():
    f = fencing.fence_ad_groups({"pricing": ["crm pricing", "crm cost"], "demo": ["crm demo", "crm pricing"]})
    assert ("crm cost", "EXACT") in f["demo"] and ("crm pricing", "EXACT") not in f["demo"]
    lists = fencing.shared_lists(["acme"], [{"name": "Rival", "common_word": True}])
    assert ("acmes", "PHRASE") in lists["brand_terms"]["negatives"]
    assert ("free", "PHRASE") in lists["junk"]["negatives"]
    assert fencing.competitor_match_types("Rival", True) == ["PHRASE", "EXACT"]
    errs = fencing.check_negatives([("free", "BROAD"), ("pricing", "PHRASE")], ["crm pricing"])
    assert len(errs) == 2


def test_audit_score_measurement_counts_double():
    r = audit.score({"A1": "fail", "A2": "pass"})
    assert r["setup_health_pct"] == pytest.approx(100 * 2 / 6, abs=0.1)
    assert r["tracking_warning"]
    r = audit.score({"A2": "pass", "A9": "fail"}, channels_on=set())
    assert r["setup_health_pct"] == 100


def test_targets_extras():
    assert targets.stage_values(30000, {"mql": 0.05})["mql"] == 1500
    t = targets.first_target(200, 150, 0.15)
    assert t["steps"][-1] == 150 and all(b < a for a, b in zip([200] + t["steps"], t["steps"]))
    assert targets.ready_for_target(20)["ready"] is False


# ---- CLI ----
def _cli(*args):
    r = subprocess.run([sys.executable, "-m", "perfos.cli", *args], cwd=SHARED, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_cli_terms_example():
    out = _cli("terms", "--csv", "examples/search_terms.csv", "--goals", "examples/goals.json")
    by = {r["item"]: r["verdict"] for r in out["rows"]}
    assert by["free crm template"] == "cut" and by["crm for agencies"] == "promote"


def test_cli_diagnose_and_name():
    d = _cli("diagnose", "--kpi", "cpa", "--actual", '{"cost": 5500, "clicks": 2500, "conversions": 100}',
             "--base", '{"cost": 5000, "clicks": 2500, "conversions": 125}')
    assert "click to conversion rate drove" in d["sentence"]
    assert _cli("name", "--channel", "search", "--type", "nonbrand", "--theme", "Budget Optimizer",
                "--geo", "us", "--language", "en")["name"] == "search|nonbrand|budget_optimizer|us|en"


def test_build_plan_check_offline():
    sys.path.insert(0, str(SHARED / "ads_scripts"))
    import google_build
    plan = json.loads((SHARED / "examples" / "search_plan.json").read_text())
    errs, warns = google_build.check(plan)
    assert errs == []
    plan["campaigns"][0]["negatives"] = [["free", "BROAD"]]
    plan["campaigns"][0]["ad_groups"][0]["headlines"][0] = "x" * 31
    errs, _ = google_build.check(plan)
    assert any("broad negative" in e for e in errs) and any("over 30" in e for e in errs)
