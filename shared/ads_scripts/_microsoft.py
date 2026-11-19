"""Microsoft Advertising API access from YOUR credentials. Nothing here talks to Redavio.

Direct API use needs your own Microsoft Advertising developer token (Microsoft Advertising UI:
Tools > Developer portal) and your own OAuth app (an Entra app registration: client ID, and a
secret for web apps). Google needs its own developer token too (see _google.py). No tokens at all?
Use the Redavio connector (https://app.redavio.com/mcp) instead.

Environment variables:
  MS_ADS_DEVELOPER_TOKEN, MS_ADS_CLIENT_ID (your Entra app), optional MS_ADS_CLIENT_SECRET,
  MS_ADS_REFRESH_TOKEN (first run), MS_ADS_CUSTOMER_ID (manager/customer), MS_ADS_ACCOUNT_ID
Microsoft rotates the refresh token on every use: the new one is saved to MS_ADS_TOKEN_FILE
(default ~/.msads_refresh_token) and read from there next time. Lose it and you sign in again.
Install: pip install bingads
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

TOKEN_FILE = Path(os.environ.get("MS_ADS_TOKEN_FILE", str(Path.home() / ".msads_refresh_token")))


def account_id(arg=None) -> int:
    v = str(arg or os.environ.get("MS_ADS_ACCOUNT_ID") or "").strip()
    if not v.isdigit():
        sys.exit("Give the Microsoft Ads account: --account-id 123456789 or MS_ADS_ACCOUNT_ID.")
    return int(v)


def _need(name):
    v = os.environ.get(name)
    if not v:
        sys.exit(f"Set {name} (see the top of _microsoft.py).")
    return v


def auth(acct: int | None = None):
    try:
        from bingads.authorization import AuthorizationData, OAuthDesktopMobileAuthCodeGrant, OAuthWebAuthCodeGrant
    except ImportError:
        sys.exit("pip install bingads")
    secret = os.environ.get("MS_ADS_CLIENT_SECRET")
    cid = _need("MS_ADS_CLIENT_ID")
    if secret:
        oauth = OAuthWebAuthCodeGrant(client_id=cid, client_secret=secret,
                                      redirect_uri=os.environ.get("MS_ADS_REDIRECT_URI", "http://localhost"))
    else:
        oauth = OAuthDesktopMobileAuthCodeGrant(client_id=cid)

    def save(tokens):  # rotated on every use: persist it or the next run fails
        TOKEN_FILE.write_text(tokens.refresh_token)
        TOKEN_FILE.chmod(0o600)
    oauth.token_refreshed_callback = save
    refresh = TOKEN_FILE.read_text().strip() if TOKEN_FILE.exists() else _need("MS_ADS_REFRESH_TOKEN")
    oauth.request_oauth_tokens_by_refresh_token(refresh)
    ad = AuthorizationData(account_id=acct or account_id(), customer_id=int(_need("MS_ADS_CUSTOMER_ID")),
                           developer_token=_need("MS_ADS_DEVELOPER_TOKEN"), authentication=oauth)
    return ad


def service(name: str, ad):
    from bingads.service_client import ServiceClient
    return ServiceClient(service=name, version=13, authorization_data=ad, environment="production")


def factory_tools(cm):
    """new(type, **fields) with every field nulled first (suds sends defaults otherwise), arr(type, items)."""
    F = cm.factory

    def new(t, **kw):
        o = F.create(t)
        for k in o.__keylist__:
            setattr(o, k, None)
        for k, v in kw.items():
            setattr(o, k, v)
        return o

    def arr(t, items):
        x = F.create(f"ArrayOf{t}")
        getattr(x, t).extend(items)
        return x
    return new, arr


def items(obj, *path) -> list:
    for p in path:
        obj = getattr(obj, p, None) if obj is not None else None
    return [x for x in (obj or []) if x is not None]


def check(label, response):
    """Raise on partial errors (Microsoft reports per-item failures inside a 'success')."""
    errs = []
    for attr in ("PartialErrors", "NestedPartialErrors"):
        pe = getattr(response, attr, None)
        for e in (getattr(pe, "BatchError", None) or getattr(pe, "BatchErrorCollection", None) or []):
            if e is not None:
                errs.append(f"{getattr(e, 'ErrorCode', '?')}: {getattr(e, 'Message', '')}")
    if errs:
        sys.exit(f"FAILED {label}: " + "; ".join(errs[:8]))
    return response
