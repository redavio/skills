"""Google Ads API access from YOUR credentials. Nothing here talks to Redavio.

Direct API use needs your own Google Ads developer token (apply in your manager account:
Admin > API Center) and your own OAuth app credentials (client ID and secret from a Google Cloud
project). Using Microsoft too needs a Microsoft Advertising developer token as well (see _microsoft.py).
No tokens at all? Use the Redavio connector (https://app.redavio.com/mcp) instead. Credentials are read, in order, from:
  1. GOOGLE_ADS_CONFIGURATION_FILE_PATH, ./google-ads.yaml or ~/google-ads.yaml
  2. environment variables: GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
     GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN, optional GOOGLE_ADS_LOGIN_CUSTOMER_ID
     (your manager account ID, digits only)
The account to work on: --customer-id or GOOGLE_ADS_CUSTOMER_ID (digits only).
Install: pip install google-ads
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def customer_id(arg: str | None = None) -> str:
    cid = (arg or os.environ.get("GOOGLE_ADS_CUSTOMER_ID") or "").replace("-", "").strip()
    if not cid.isdigit():
        sys.exit("Give the Google Ads account: --customer-id 1234567890 or GOOGLE_ADS_CUSTOMER_ID.")
    return cid


def client():
    try:
        from google.ads.googleads.client import GoogleAdsClient
    except ImportError:
        sys.exit("pip install google-ads")
    for p in (os.environ.get("GOOGLE_ADS_CONFIGURATION_FILE_PATH"), "google-ads.yaml",
              str(Path.home() / "google-ads.yaml")):
        if p and Path(p).exists():
            return GoogleAdsClient.load_from_storage(p)
    if not os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN"):
        sys.exit("No Google Ads credentials: add google-ads.yaml or set GOOGLE_ADS_* env vars "
                 "(a developer token is required for direct API calls).")
    os.environ.setdefault("GOOGLE_ADS_USE_PROTO_PLUS", "True")
    return GoogleAdsClient.load_from_env()


def query(gac, cid: str, gaql: str) -> list:
    svc = gac.get_service("GoogleAdsService")  # keep a reference: a temporary service can be GC'd mid-stream
    return [r for batch in svc.search_stream(customer_id=cid, query=gaql) for r in batch.results]


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")
