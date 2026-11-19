"""Campaign naming convention: channel|type|theme|geo|language (context/build.md A3).

The segment (brand, nonbrand, competitor, pmax) is read from the name so every report
splits brand and non-brand without manual tagging. Unknown names return None: the
caller must decide, never guess.
"""
from __future__ import annotations


def parse(name: str) -> dict | None:
    parts = [p.strip().lower() for p in (name or "").split("|")]
    if len(parts) < 2:
        return None
    keys = ["channel", "type", "theme", "geo", "language"]
    return dict(zip(keys, parts))


def segment(name: str, channel_type: str | None = None) -> str | None:
    """Return brand | nonbrand | competitor | pmax, or None if it can't be told."""
    if channel_type and channel_type.upper() in ("PERFORMANCE_MAX", "PERFORMANCEMAX"):
        return "pmax"
    p = parse(name)
    if not p:
        return None
    if p["channel"] == "pmax":
        return "pmax"
    t = p.get("type", "")
    if t in ("brand", "nonbrand", "competitor"):
        return t
    if t in ("non_brand", "non-brand"):
        return "nonbrand"
    return None
