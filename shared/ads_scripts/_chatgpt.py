"""Read-only client for OpenAI's Ads API (https://api.ads.openai.com/v1). Standard library only.

OpenAI's keys can't be limited to reading, so this client is: it only sends GET. Anything that would
change an account is refused here, on purpose. Key: OPENAI_ADS_API_KEY (Ads Manager > Settings > General
> API Keys; one key per ad account). Keep it server-side; never paste it in a browser or a chat.
"""
from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.ads.openai.com/v1"
PARTNER_ONLY = ("Some features (pixel and Conversions API key creation, conversion bidding, brand updates) "
                "are switched on per account by OpenAI. Ask your OpenAI partner rep to enable it")




def _ssl_context():
    """Python from python.org on a Mac ships without root certificates; use certifi's when it's installed."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


class Client:
    def __init__(self, key: str | None = None, base: str = BASE):
        self.key = key or os.environ.get("OPENAI_ADS_API_KEY")
        if not self.key:
            raise SystemExit("Set OPENAI_ADS_API_KEY to an Ads API key (Ads Manager > Settings > General > API Keys).")
        self.base = base.rstrip("/")

    def request(self, method: str, path: str, params: dict | None = None) -> dict:
        if method.upper() != "GET":
            raise PermissionError(f"{method} {path} refused: this client is read only. "
                                  "Changes are made by a person in Ads Manager, or an app after they click apply.")
        q = urllib.parse.urlencode(params or {}, doseq=True)
        req = urllib.request.Request(f"{self.base}{path}{'?' + q if q else ''}",
                                     headers={"Authorization": f"Bearer {self.key}", "Accept": "application/json",
                                              "User-Agent": "redavio-skills/1.0 (+https://github.com/redavio/skills)"})
        try:
            with urllib.request.urlopen(req, timeout=60, context=_ssl_context()) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            try:
                msg = json.loads(e.read().decode()).get("error", {}).get("message", "")
            except Exception:
                msg = ""
            if e.code == 401:
                raise RuntimeError("The API key was refused (401). Check it's an Ads API key for this ad account.") from None
            if e.code in (403, 404):
                raise RuntimeError(f"{e.code} on {path}. {PARTNER_ONLY}, or check the ID. {msg}".strip()) from None
            if e.code == 429:
                raise RuntimeError("Rate limited (429): 600 requests a minute per endpoint. Wait a minute and retry.") from None
            raise RuntimeError(f"OpenAI Ads API error {e.code} on {path}: {msg}") from None
        except urllib.error.URLError as e:
            if "CERTIFICATE_VERIFY_FAILED" in str(e.reason):
                raise RuntimeError("Python can't verify HTTPS certificates. Run: pip install certifi "
                                   "(or, on a Mac, open 'Install Certificates.command' in your Python folder).") from None
            raise RuntimeError(f"Couldn't reach the OpenAI Ads API: {e.reason}") from None

    def get(self, path: str, params: dict | None = None) -> dict:
        return self.request("GET", path, params)

    def get_all(self, path: str, params: dict | None = None, limit: int = 100) -> list[dict]:
        """Every item of a list endpoint, following the after cursor."""
        out, p = [], {**(params or {}), "limit": limit}
        while True:
            page = self.get(path, p)
            out += page.get("data", [])
            if not page.get("has_more"):
                return out
            p = {**p, "after": page.get("last_id")}


def insight_rows(api_rows: list[dict], campaign: str, ad_group: str, cluster: str = "") -> list[dict]:
    """Insights rows (readable_time, impressions, clicks, spend, conversions) -> the weekly review's columns.
    Spend comes back in currency units (12.50 = $12.50), not micros."""
    return [{"week": r.get("readable_time", ""), "campaign": campaign, "ad_group": ad_group, "cluster": cluster,
             "impressions": r.get("impressions", 0), "clicks": r.get("clicks", 0),
             "spend": r.get("spend", 0), "conversions": r.get("conversions", 0)} for r in api_rows]
