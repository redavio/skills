"""ChatGPT ads: limits, context hints, plan, weekly review (planted signal), bulk job, channel comparison,
and the read-only API client. Sample data: shared/examples/chatgpt_* (fictional B2B SaaS)."""
import csv
import io
import json
import sys
import urllib.error
from pathlib import Path

import pytest

from perfos import chatgpt

SHARED = Path(__file__).resolve().parents[1]
EX = SHARED / "examples"
sys.path.insert(0, str(SHARED / "ads_scripts"))
import _chatgpt  # noqa: E402


def rows(name):
    with open(EX / name, newline="") as f:
        return list(csv.DictReader(f))


GOOD = {"title": "Forecast pipeline from every campaign",
        "body": "See which campaigns create pipeline, not just leads.",
        "target_url": "https://www.example.com/demo"}


# --- Ad copy limits (chat card) ---

def test_good_card_passes():
    assert chatgpt.check_card(GOOD) == []


def test_card_over_limits():
    errs = chatgpt.check_card({"title": "x" * 51, "body": "y" * 101, "target_url": "ftp://example.com"})
    text = " | ".join(errs)
    assert "title" in text and "51" in text
    assert "body" in text and "101" in text
    assert "http" in text


def test_card_title_too_short_and_missing_fields():
    assert any("title" in e for e in chatgpt.check_card({**GOOD, "title": "Hi"}))
    assert any("target_url" in e for e in chatgpt.check_card({"title": "Fine title", "body": "ok"}))


def test_card_images():
    assert any("640" in e for e in chatgpt.check_card({**GOOD, "images": [{"width": 600, "height": 600}]}))
    three = [{"width": 800, "height": 800}] * 3
    assert any("4" in e and "6" in e for e in chatgpt.check_card({**GOOD, "images": three}))
    mixed = [{"width": 800, "height": 800}] * 3 + [{"width": 1200, "height": 800}]
    assert any("square" in e for e in chatgpt.check_card({**GOOD, "images": mixed}))
    assert chatgpt.check_card({**GOOD, "images": [{"width": 1280, "height": 720}]}) == []


# --- Context hints ---

def test_hints_need_a_cluster_and_stay_under_the_limit():
    out = chatgpt.check_hints([
        {"ad_group": "A", "cluster": "", "hints": ["pipeline forecasting"]},
        {"ad_group": "B", "cluster": "forecasting", "hints": [f"hint {i}" for i in range(2001)]},
        {"ad_group": "C", "cluster": "attribution", "hints": ["b2b attribution"]},
    ])
    by = {g["ad_group"]: g for g in out["groups"]}
    assert any("cluster" in p for p in by["A"]["problems"])
    assert any("2,000" in p for p in by["B"]["problems"])
    assert by["C"]["problems"] == []
    assert out["ok"] is False


def test_hints_are_not_keywords():
    out = chatgpt.check_hints([{"ad_group": "A", "cluster": "crm",
                                "hints": ["[crm software]", '"crm"', "+crm", "CRM tools", "crm tools", ""]}])
    probs = " | ".join(out["groups"][0]["problems"])
    assert "match type" in probs
    assert "duplicate" in probs
    assert "empty" in probs
    assert out["groups"][0]["hints"] == ["crm software", "crm", "CRM tools"]  # first spelling kept


# --- Plan ---

def test_plan_on_cpm():
    p = chatgpt.plan(monthly_budget=3000, objective="impressions", cpm=60, ctr=0.007, cvr=0.02)
    assert p["impressions"] == 50000
    assert p["clicks"] == 350
    assert p["conversions"] == pytest.approx(7)
    assert p["cpa"] == pytest.approx(3000 / 7)
    assert p["daily_budget"] == pytest.approx(100)
    assert p["max_bid_micros"] == 60000  # $60 CPM is bid per impression


def test_plan_on_cpc():
    p = chatgpt.plan(monthly_budget=3000, objective="clicks", cpc=2.5, ctr=0.007, cvr=0.02)
    assert p["clicks"] == 1200
    assert p["max_bid_micros"] == 2_500_000


def test_conversion_bidding_waits_for_data():
    thin = chatgpt.plan(monthly_budget=3000, objective="conversions", cpc=2.5, ctr=0.007, cvr=0.02, conversions_30d=12)
    assert thin["conversion_bidding"]["ready"] is False
    assert thin["objective"] == "clicks"
    assert "30" in thin["conversion_bidding"]["reason"]
    ready = chatgpt.plan(monthly_budget=3000, objective="conversions", cpc=2.5, ctr=0.007, cvr=0.02, conversions_30d=40)
    assert ready["objective"] == "conversions" and ready["conversion_bidding"]["ready"] is True


@pytest.mark.parametrize("kw, words", [
    ({"monthly_budget": 0}, "budget"),
    ({"ctr": 7}, "0.007"),
    ({"objective": "reach"}, "impressions, clicks, conversions"),
    ({"cpm": None, "cpc": None}, "cpm or cpc"),
])
def test_plan_bad_input_is_plain_english(kw, words):
    args = {"monthly_budget": 3000, "objective": "clicks", "cpc": 2.5, "cpm": None, "ctr": 0.007, "cvr": 0.02, **kw}
    with pytest.raises(ValueError, match=words.replace(".", r"\.")):
        chatgpt.plan(**args)


# --- Weekly review: the planted signal ---

def test_weekly_finds_the_planted_signal_and_nothing_else():
    out = chatgpt.weekly(rows("chatgpt_insights.csv"), ads=rows("chatgpt_ads.csv"))
    acting = [g for g in out["ad_groups"] if g["action"] in ("cut", "flag")]
    assert [g["ad_group"] for g in acting] == ["Broad - AI tools"]
    assert acting[0]["cpa_vs_account"] >= 2.5
    assert acting[0]["cluster"] == "ai-marketing-tools"
    assert [a["ad"] for a in out["ad_problems"]] == ["Forecast card B"]
    assert "54" in out["ad_problems"][0]["problems"][0]
    assert out["account"]["conversions"] == 152


def test_weekly_every_group_carries_its_cluster():
    out = chatgpt.weekly(rows("chatgpt_insights.csv"))
    assert all(g["cluster"] for g in out["ad_groups"])


def test_weekly_empty_data_says_so():
    out = chatgpt.weekly([])
    assert out["empty"] is True and "no rows" in out["message"].lower()


def test_weekly_bad_number_names_the_column_and_row():
    bad = rows("chatgpt_insights.csv")[:3]
    bad[1]["spend"] = "abc"
    with pytest.raises(ValueError, match=r"spend.*row 2"):
        chatgpt.weekly(bad)


def test_weekly_missing_column():
    with pytest.raises(ValueError, match="clicks"):
        chatgpt.weekly([{"week": "2026-09-21", "ad_group": "A", "spend": "10", "conversions": "1"}])


# --- Build: a bulk job, paused, never sent by us ---

def test_bulk_job_is_paused_linked_and_in_micros():
    job = chatgpt.bulk_job(json.loads((EX / "chatgpt_build.json").read_text()))
    assert job["validate_only"] is True
    ops = job["operations"]
    assert [o["type"] for o in ops] == ["campaign.create", "ad_group.create", "ad.create", "ad_group.create", "ad.create"]
    assert all(o["input"]["status"] == "paused" for o in ops)
    assert len({o["idempotency_key"] for o in ops}) == len(ops)
    assert len({o["operation_id"] for o in ops}) == len(ops)
    camp, group, ad = ops[0], ops[1], ops[2]
    assert camp["input"]["max_budget_micros"] == 100_000_000
    assert camp["input"]["target_countries"] == ["US"]
    assert group["input"]["campaign_idempotency_key"] == camp["idempotency_key"]
    assert group["input"]["max_bid_micros"] == 3_000_000
    assert group["input"]["context_hints"][0] == "forecast B2B pipeline from ad spend"
    assert ad["input"]["ad_group_idempotency_key"] == group["idempotency_key"]
    assert ad["input"]["source_image_url"].startswith("https://")
    assert job["clusters"] == {"Pipeline forecasting": "forecasting", "Attribution": "attribution"}


def test_bulk_job_is_stable():
    plan = json.loads((EX / "chatgpt_build.json").read_text())
    assert chatgpt.bulk_job(plan) == chatgpt.bulk_job(plan)


def test_bulk_job_refuses_bad_copy_or_hints():
    plan = json.loads((EX / "chatgpt_build.json").read_text())
    plan["ad_groups"][0]["ads"][0]["title"] = "x" * 60
    with pytest.raises(ValueError, match="title"):
        chatgpt.bulk_job(plan)
    plan = json.loads((EX / "chatgpt_build.json").read_text())
    plan["ad_groups"][1]["cluster"] = ""
    with pytest.raises(ValueError, match="cluster"):
        chatgpt.bulk_job(plan)


# --- Measure: ChatGPT next to search ---

def test_compare_ranks_on_pipeline_and_warns_on_windows():
    out = chatgpt.compare([
        {"channel": "Google Ads", "spend": 20000, "conversions": 200, "pipeline": 400000, "click_window_days": 30, "view_window_days": 0},
        {"channel": "ChatGPT ads", "spend": 5000, "conversions": 25, "pipeline": 50000, "click_window_days": 30, "view_window_days": 1},
    ])
    assert [c["channel"] for c in out["channels"]] == ["Google Ads", "ChatGPT ads"]
    gpt = out["channels"][1]
    assert gpt["cpa"] == pytest.approx(200) and gpt["cost_per_pipeline_dollar"] == pytest.approx(0.10)
    assert any("view" in w for w in out["warnings"])


def test_compare_no_pipeline_falls_back_to_cpa():
    out = chatgpt.compare([{"channel": "A", "spend": 100, "conversions": 4}, {"channel": "B", "spend": 100, "conversions": 2}])
    assert [c["channel"] for c in out["channels"]] == ["A", "B"]
    assert any("pipeline" in w for w in out["warnings"])


# --- Read-only API client ---

def test_client_refuses_writes():
    c = _chatgpt.Client("test-key")
    for m in ("POST", "PATCH", "DELETE", "PUT"):
        with pytest.raises(PermissionError, match="read only"):
            c.request(m, "/campaigns")


def test_client_needs_a_key(monkeypatch):
    monkeypatch.delenv("OPENAI_ADS_API_KEY", raising=False)
    with pytest.raises(SystemExit, match="OPENAI_ADS_API_KEY"):
        _chatgpt.Client()


def test_client_partner_only_errors_are_plain(monkeypatch):
    def boom(req, timeout=0, context=None):
        raise urllib.error.HTTPError(req.full_url, 403, "Forbidden", {}, io.BytesIO(b'{"error":{"message":"no"}}'))
    monkeypatch.setattr(_chatgpt.urllib.request, "urlopen", boom)
    with pytest.raises(RuntimeError, match="partner"):
        _chatgpt.Client("k").get("/conversions/api_keys")


def test_client_pages_through_lists(monkeypatch):
    pages = iter([{"object": "list", "data": [{"id": "a"}], "has_more": True, "last_id": "a"},
                  {"object": "list", "data": [{"id": "b"}], "has_more": False, "last_id": "b"}])
    seen = []

    def fake(req, timeout=0, context=None):
        seen.append(req.full_url)
        return io.BytesIO(json.dumps(next(pages)).encode())
    monkeypatch.setattr(_chatgpt.urllib.request, "urlopen", fake)
    assert [r["id"] for r in _chatgpt.Client("k").get_all("/campaigns")] == ["a", "b"]
    assert "after=a" in seen[1]


def test_insight_rows_match_the_weekly_columns():
    api = [{"readable_time": "2026-09-21", "impressions": 1000, "clicks": 7, "spend": 21.5, "conversions": 1}]
    out = _chatgpt.insight_rows(api, campaign="c", ad_group="g", cluster="forecasting")
    assert out == [{"week": "2026-09-21", "campaign": "c", "ad_group": "g", "cluster": "forecasting",
                    "impressions": 1000, "clicks": 7, "spend": 21.5, "conversions": 1}]
