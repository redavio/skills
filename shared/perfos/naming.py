"""The naming and UTM standard (shared/NAMING.md): campaigns are channel|segment|theme|geo|language.

The segment (brand, nonbrand, competitor, pmax, prospecting, retargeting) is read from the name so every
report splits them without manual tagging. Unknown names return None: the caller must decide, never guess.
"""
from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

CHANNELS = ("search", "pmax", "demandgen", "youtube", "audience", "chatgpt", "linkedin")
SEGMENTS = ("brand", "nonbrand", "competitor", "prospecting", "retargeting", "aware", "engaged")
STANDARD = re.compile(rf"^({'|'.join(CHANNELS)})\|({'|'.join(SEGMENTS)})\|[a-z0-9_]+\|[a-z0-9_]+\|[a-z]{{2,3}}$")
LEGACY = {
    "search | brand": "search|brand|core|us|en",
    "search | non-brand": "search|nonbrand|core|us|en",
    "search | non-brand | ai max": "search|nonbrand|core_aimax|us|en",
    "search | competitor": "search|competitor|core|us|en",
    "pmax | non-brand": "pmax|nonbrand|core|us|en",
    "portfolio | brand": "portfolio|brand",
    "portfolio | non-brand": "portfolio|nonbrand",
    "portfolio | non-brand | ai max": "portfolio|nonbrand|aimax",
    "portfolio | competitor": "portfolio|competitor",
    "junk intent": "negatives|junk",
}
MEDIUM = {"search": "cpc", "pmax": "cpc", "chatgpt": "cpc", "demandgen": "display", "audience": "display",
          "youtube": "video", "linkedin": "paid_social"}


def is_standard(name: str) -> bool:
    return bool(STANDARD.match(name or ""))


def slot(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")


def standard_name(name: str) -> str | None:
    """The standard name for a campaign, portfolio or negative list, or None if it can't be told."""
    if is_standard(name) or re.match(r"^(portfolio|negatives)\|[a-z0-9_|]+$", name or ""):
        return name
    return LEGACY.get(re.sub(r"\s+", " ", (name or "").strip().lower()))


def cmp(name: str) -> str:
    """utm_campaign value: the campaign name with | -> -."""
    return name.replace("|", "-")


def with_utms(url: str, campaign: str, source: str, content: str | None = None) -> str:
    """Add the standard UTMs to a landing URL (ChatGPT ads and anything else without a URL suffix).
    Leaves a URL that already has utm_source alone."""
    parts = urlsplit(url)
    q = parse_qsl(parts.query, keep_blank_values=True)
    if any(k == "utm_source" for k, _ in q):
        return url
    channel = (parse(campaign) or {}).get("channel", "")
    q += [("utm_source", source), ("utm_medium", MEDIUM.get(channel, "cpc")), ("utm_campaign", cmp(campaign))]
    if content:
        q.append(("utm_content", slot(content)))
    return urlunsplit(parts._replace(query=urlencode(q, safe="{}")))


def parse(name: str) -> dict | None:
    parts = [p.strip().lower() for p in (name or "").split("|")]
    if len(parts) < 2:
        return None
    keys = ["channel", "type", "theme", "geo", "language"]
    return dict(zip(keys, parts))


def segment(name: str, channel_type: str | None = None) -> str | None:
    """Return brand | nonbrand | competitor | pmax | prospecting | retargeting, or None if it can't be told."""
    if channel_type and channel_type.upper() in ("PERFORMANCE_MAX", "PERFORMANCEMAX"):
        return "pmax"
    p = parse(name)
    if not p:
        return None
    if p["channel"] == "pmax":
        return "pmax"
    t = p.get("type", "")
    if t in ("brand", "nonbrand", "competitor", "prospecting", "retargeting"):
        return t
    if t in ("non_brand", "non-brand"):
        return "nonbrand"
    return None
