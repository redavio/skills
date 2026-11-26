"""LinkedIn Ads math (perfos.linkedin), behind the linkedin-* skills."""
import pytest

from perfos import linkedin as li

URL = ("https://x.com/signup?utm_source=linkedin&utm_medium=paid_social"
       "&utm_campaign=linkedin-aware-icp-us-en&utm_content=video")


def test_ad_copy_errors_block_and_long_text_warns():
    ok = li.check_ad({"format": "video", "intro": "Short intro.", "headline": "A headline", "cta": "learn_more",
                      "landing_url": URL, "campaign": "linkedin|aware|icp|us|en"})
    assert ok["errors"] == [] and ok["warnings"] == []
    bad = li.check_ad({"format": "single_image", "intro": "x" * 601, "headline": "", "cta": "CLICK",
                       "landing_url": "http://x.com"})
    assert len(bad["errors"]) == 4
    warn = li.check_ad({"intro": "x" * 200, "headline": "y" * 80, "landing_url": URL})
    assert warn["errors"] == [] and len(warn["warnings"]) == 2


def test_thought_leader_ads_need_no_copy_and_documents_no_headline():
    assert li.check_ad({"format": "thought_leader"})["errors"] == []
    assert li.check_ad({"format": "document", "intro": "Read the guide.", "landing_url": URL})["errors"] == []


def test_utms_follow_the_naming_standard():
    assert li.check_utms(URL, "linkedin|aware|icp|us|en") == []
    probs = li.check_utms("https://x.com?utm_source=LinkedIn&utm_medium=cpc&utm_campaign=other", "linkedin|aware|icp|us|en")
    assert len(probs) == 4


def test_tracking_needs_tag_conversion_and_utms():
    good = li.check_tracking({"insight_tag": "10486644", "conversions": [{"name": "Free signup"}],
                              "landing_urls": [{"campaign": "linkedin|aware|icp|us|en", "url": URL}]})
    assert good["ok"] and good["conversions"] == ["Free signup"]
    bad = li.check_tracking({"insight_tag": "", "conversions": [{"name": "x", "enabled": False}]})
    assert not bad["ok"] and len(bad["problems"]) == 2


def test_target_accounts_cleaned_and_loose_matches_flagged():
    c = li.clean_accounts(["Acme, Inc.", "acme", "  Globex  LLC", ""])
    assert c["accounts"] == ["Acme", "Globex"] and c["duplicates"] == ["acme"]
    m = li.check_matches([{"company_name": "Funnel", "matched_name": "Funnel"},
                          {"company_name": "Swydo", "matched_name": "Swydo Reporting Software BV"},
                          {"company_name": "Nope", "matched_name": None}])
    assert m["found"] == 2 and m["missing"] == ["Nope"] and m["check"][0]["company"] == "Swydo"


def test_plan_flags_thin_audiences_and_budget_minimums():
    p = li.plan([{"name": "linkedin|aware|target_accounts|us|en", "members": 320,
                  "ad_sets": [{"name": "a", "daily_budget": 10}, {"name": "b", "daily_budget": 10}]},
                 {"name": "linkedin|aware|icp|us|en", "members": 300_000, "ad_sets": [{"name": "c", "daily_budget": 5}]}])
    t = p["campaigns"][0]
    assert t["monthly_budget"] == 600 and t["impressions"] == round(600 / 35 * 1000)
    assert t["weekly_frequency"] > li.MAX_WEEKLY_FREQ
    joined = " ".join(p["problems"])
    assert "under 50,000" in joined and "wears the audience out" in joined and "under LinkedIn's $10 minimum" in joined
    # Never suggests a budget below LinkedIn's minimum: widen instead.
    freq_msg = next(x for x in p["problems"] if "wears the audience out" in x)
    assert "minimum for its ad sets is still too much" in freq_msg and "Lower the budget" not in freq_msg
    with pytest.raises(ValueError):
        li.plan([])


def _rows(ad_set, weeks):
    return [{"week": f"2026-10-{5 + 7 * i:02d}", "campaign": ad_set.rsplit("|", 1)[0], "ad_set": ad_set,
             "format": ad_set.rsplit("|", 1)[1], "impressions": imp, "clicks": clk, "spend": sp, "conversions": cv}
            for i, (imp, clk, sp, cv) in enumerate(weeks)]


def test_weekly_refresh_frequency_and_volume_gate():
    rows = (_rows("linkedin|aware|icp|us|en|video", [(10000, 60, 350, 0), (10000, 55, 350, 0), (10000, 20, 350, 0)])
            + _rows("linkedin|aware|target_accounts|us|en|single_image", [(2000, 10, 80, 0), (2000, 10, 80, 0), (2000, 10, 80, 0)])
            + _rows("linkedin|engaged|all|us|en|document", [(3000, 300, 300, 0), (3000, 300, 300, 0), (3000, 300, 300, 0)])
            + _rows("linkedin|engaged|all|us|en|single_image", [(3000, 300, 300, 12), (3000, 300, 300, 12), (3000, 300, 300, 12)]))
    w = li.weekly(rows, audiences=[{"campaign": "linkedin|aware|target_accounts|us|en", "members": 320}])
    by = {a["ad_set"]: a for a in w["ad_sets"]}
    assert by["linkedin|aware|icp|us|en|video"]["action"] == "refresh"
    assert by["linkedin|aware|target_accounts|us|en|single_image"]["action"] == "flag"
    assert by["linkedin|engaged|all|us|en|document"]["action"] == "cut"
    assert w["ad_sets"][0]["action"] == "cut"
    # The CPA benchmark is the engaged campaign's own, never diluted by awareness spend.
    assert w["account"]["engaged_cpa"] == 1800 / 36
    assert li.weekly([])["empty"]


def test_holdout_split_is_repeatable_and_balanced():
    names = [f"Company {i}" for i in range(200)]
    a, b = li.holdout_split(names), li.holdout_split(list(reversed(names)))
    assert a["holdout"] == b["holdout"]
    assert 70 <= a["counts"]["holdout"] <= 130 and a["counts"]["test"] + a["counts"]["holdout"] == 200
    with pytest.raises(ValueError):
        li.holdout_split(names, 0.9)


def test_measure_compares_reached_with_not_reached():
    accts = ([{"account": f"r{i}", "impressions": 500, "opportunities": 1 if i < 30 else 0, "pipeline": 20000 if i < 30 else 0}
              for i in range(100)]
             + [{"account": f"n{i}", "impressions": 0, "opportunities": 1 if i < 10 else 0, "pipeline": 20000 if i < 10 else 0}
                for i in range(100)])
    m = li.measure(accts)
    assert m["reached"]["opportunity_rate"] == 0.3 and m["not_reached"]["opportunity_rate"] == 0.1
    assert m["opportunity_lift"] == 2.0 and m["significance"]["verdict"] == "won"
