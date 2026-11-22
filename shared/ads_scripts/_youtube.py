"""YouTube Data API access from YOUR OAuth client, for video ads. Nothing here talks to Redavio.

Google Ads can't host a video: every video ad points at a YouTube video. These helpers upload your video
ads to your own channel as UNLISTED (not searchable, not on the channel page; Google Ads can still run them).

Your own OAuth client, once (about 5 minutes):
  1. console.cloud.google.com: create a project, enable "YouTube Data API v3".
  2. Google Auth Platform > Audience: External, publishing status Testing, add your Google account as a
     test user. Testing needs no Google review (up to 100 test users; you sign in again every 7 days).
  3. Clients > Create client > Desktop app > download the JSON (client_secret_*.json).
Scopes asked for: youtube.upload and youtube.readonly. Nothing else on the channel is read, changed or deleted.
Install: pip install google-api-python-client google-auth-oauthlib
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]
TOKEN = Path.home() / ".redavio" / "youtube_token.json"
SHAPES = {"video_horizontal": "16:9", "video_vertical": "9:16", "video_square": "1:1"}
LIMITS = {"headline": 40, "long_headline": 90, "description": 90, "business_name": 25}


def video_body(title: str, fmt: str, description: str = "") -> dict:
    """An unlisted upload's metadata. Pure."""
    return {"snippet": {"title": f"{title} ({SHAPES[fmt]})"[:100], "description": description[:4900], "categoryId": "28"},
            "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": False}}


def results(channel_id: str | None, ids: dict[str, str | None]) -> dict:
    """The video.json the dashboard reads (scripts/from_portal.mjs), same shape as Redavio's
    paid_display_youtube MCP tool. Pure."""
    return {"connected": bool(channel_id), "channel_id": channel_id,
            "videos": {f: {"youtube_id": ids.get(f)} for f in SHAPES if f in ids}}


def video_ad_problems(video_ids: list[str], headlines: list[str], long_headlines: list[str], descriptions: list[str],
                      business_name: str, final_url: str) -> list[str]:
    """What Google would refuse in a Demand Gen video ad, said plainly before any API call. Pure."""
    out = []
    if not video_ids:
        out.append("Give at least one --video-id (the 11-character id after youtu.be/).")
    out += [f"'{v}' isn't a YouTube video id (11 characters)." for v in video_ids if len(v) != 11]
    for name, items, need in (("headline", headlines, 1), ("long_headline", long_headlines, 1), ("description", descriptions, 1)):
        if len(items) < need:
            out.append(f"Give at least one --{name.replace('_', '-')}.")
        if len(items) > 5:
            out.append(f"At most 5 of --{name.replace('_', '-')}.")
        out += [f"{name.replace('_', ' ').capitalize()} over {LIMITS[name]} characters: '{t}'" for t in items if len(t) > LIMITS[name]]
    if not business_name:
        out.append("Give --business-name.")
    elif len(business_name) > LIMITS["business_name"]:
        out.append(f"Business name over {LIMITS['business_name']} characters.")
    if not final_url.startswith(("https://", "http://")):
        out.append("--final-url must be a full https:// address.")
    return out


def service(client_secret: str | None):
    """A signed-in YouTube client. The first run opens a browser; the token is kept in ~/.redavio/."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        sys.exit("pip install google-api-python-client google-auth-oauthlib")
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES) if TOKEN.exists() else None
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:  # noqa: BLE001 (Testing-mode tokens expire after 7 days: sign in again)
            creds = None
    if not creds or not creds.valid:
        if not client_secret:
            sys.exit("First run: give --client-secret client_secret_*.json (see the top of _youtube.py).")
        creds = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES).run_local_server(port=0)
        TOKEN.parent.mkdir(parents=True, exist_ok=True)
        TOKEN.write_text(creds.to_json())
        TOKEN.chmod(0o600)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def channel(yt) -> dict:
    items = yt.channels().list(part="snippet", mine=True).execute().get("items") or []
    if not items:
        sys.exit("That Google account has no YouTube channel. Create one at youtube.com, then run again.")
    return {"id": items[0]["id"], "title": items[0]["snippet"]["title"]}


def read_back(yt, ids: list[str]) -> dict:
    """Each video's privacy and whether YouTube has finished processing it (Google Ads needs it finished)."""
    if not ids:
        return {}
    items = yt.videos().list(part="status,processingDetails", id=",".join(ids)).execute().get("items") or []
    return {i["id"]: {"privacy": i["status"]["privacyStatus"],
                      "processing": (i.get("processingDetails") or {}).get("processingStatus", "unknown")} for i in items}


def dump(obj) -> str:
    return json.dumps(obj, indent=1)
