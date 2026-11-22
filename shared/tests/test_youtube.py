"""YouTube video ads from your own OAuth client: upload metadata, the dashboard's video.json, and the
plain-words checks before a Demand Gen video ad reaches Google."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ads_scripts"))
import _youtube as Y  # noqa: E402


def test_uploads_are_unlisted_and_named_by_shape():
    b = Y.video_body("Acme ad", "video_vertical", "Budgets that move themselves")
    assert b["status"]["privacyStatus"] == "unlisted" and b["snippet"]["title"] == "Acme ad (9:16)"


def test_results_match_the_dashboard_and_mcp_shape():
    r = Y.results("UC123", {"video_horizontal": "AAAAAAAAAAA", "video_square": None})
    assert r == {"connected": True, "channel_id": "UC123",
                 "videos": {"video_horizontal": {"youtube_id": "AAAAAAAAAAA"}, "video_square": {"youtube_id": None}}}


def test_video_ad_problems_said_before_any_api_call():
    ok = dict(video_ids=["AAAAAAAAAAA"], headlines=["Short"], long_headlines=["Longer line"], descriptions=["Desc"],
              business_name="Acme", final_url="https://acme.com")
    assert Y.video_ad_problems(**ok) == []
    bad = Y.video_ad_problems(**{**ok, "video_ids": ["https://youtu.be/x"], "headlines": ["x" * 41],
                                 "business_name": "x" * 26, "final_url": "acme.com"})
    assert any("isn't a YouTube video id" in p for p in bad)
    assert any("Headline over 40" in p for p in bad)
    assert any("Business name over 25" in p for p in bad)
    assert any("https://" in p for p in bad)
    assert "Give at least one --video-id" in Y.video_ad_problems(**{**ok, "video_ids": []})[0]
