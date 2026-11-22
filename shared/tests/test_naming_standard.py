"""The naming and UTM standard (shared/NAMING.md)."""
from perfos import naming
from perfos.chatgpt import bulk_job
from perfos.matching import match
from perfos.schema import CrmRecord
from datetime import date


def test_standard_and_legacy_names():
    assert naming.is_standard("demandgen|retargeting|core|us|en")
    assert not naming.is_standard("Search | Brand")
    assert naming.standard_name("Search | Non-Brand | AI Max") == "search|nonbrand|core_aimax|us|en"
    assert naming.standard_name("Portfolio | Non-Brand") == "portfolio|nonbrand"
    assert naming.standard_name("Some Test Campaign") is None
    assert naming.segment("audience|prospecting|core|us|en") == "prospecting"


def test_with_utms_adds_once_and_picks_medium():
    u = naming.with_utms("https://x.com/p?a=1", "chatgpt|nonbrand|core|us|en", "chatgpt", "Pipeline forecasting")
    assert u == ("https://x.com/p?a=1&utm_source=chatgpt&utm_medium=cpc&utm_campaign=chatgpt-nonbrand-core-us-en"
                 "&utm_content=pipeline_forecasting")
    assert naming.with_utms(u, "chatgpt|nonbrand|core|us|en", "chatgpt") == u
    assert "utm_medium=video" in naming.with_utms("https://x.com", "youtube|prospecting|core|us|en", "google")


def test_chatgpt_build_tags_every_ad():
    job = bulk_job({"campaign": {"name": "chatgpt|nonbrand|core|us|en", "daily_budget": 50, "countries": ["US"]},
                    "ad_groups": [{"name": "Attribution", "cluster": "attribution", "max_cpc": 2,
                                   "hints": ["how to attribute pipeline to ads", "b2b attribution model"],
                                   "ads": [{"name": "a", "title": "Attribution that holds", "body": "See what drove pipeline.",
                                            "target_url": "https://x.com/attribution", "image_url": "https://x.com/i.png"}]}]})
    ad = [o for o in job["operations"] if o["type"] == "ad.create"][0]["input"]
    assert "utm_source=chatgpt" in ad["target_url"] and "utm_campaign=chatgpt-nonbrand-core-us-en" in ad["target_url"]


def test_match_uses_campaignid_then_slug_map():
    recs = [CrmRecord("1", date(2026, 1, 1), utm_source="google", utm_campaign="search-brand-core-us-en", campaignid="111"),
            CrmRecord("2", date(2026, 1, 1), utm_source="bing", utm_campaign="search-brand-core-us-en")]
    match(recs, {}, campaign_ids={"search-brand-core-us-en": "222"})
    assert [r.campaign_id for r in recs] == ["111", "222"]
