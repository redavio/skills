"""Character and count limits for ads and assets (Google and Microsoft share these for Search).

Checked before anything is built: a build never reaches the platform with copy that will bounce.
"""
from __future__ import annotations

RSA = {"headline": 30, "description": 90, "path": 15, "headlines": (3, 15), "descriptions": (2, 4)}
ASSETS = {"sitelink_text": 25, "sitelink_description": 35, "callout": 25, "snippet_value": 25,
          "business_name": 25}
PMAX = {"headline": 30, "long_headline": 90, "description": 90, "short_description": 60,
        "headlines": (3, 15), "long_headlines": (1, 5), "descriptions": (2, 5)}
SNIPPET_HEADERS = ("Amenities", "Brands", "Courses", "Degree programs", "Destinations", "Featured hotels",
                   "Insurance coverage", "Models", "Neighborhoods", "Service catalog", "Shows", "Styles", "Types")


def check_rsa(headlines: list[str], descriptions: list[str], path1: str = "", path2: str = "",
              want_full: bool = True) -> list[str]:
    """Problems with one responsive search ad. want_full: the standard is 15 headlines, 4 descriptions."""
    errs = []
    for h in headlines:
        if len(h) > RSA["headline"]:
            errs.append(f"headline over 30 ({len(h)}): {h}")
    for d in descriptions:
        if len(d) > RSA["description"]:
            errs.append(f"description over 90 ({len(d)}): {d}")
    for p in (path1, path2):
        if p and len(p) > RSA["path"]:
            errs.append(f"path over 15: {p}")
    lo, hi = RSA["headlines"]
    if not lo <= len(headlines) <= hi:
        errs.append(f"{len(headlines)} headlines (allowed {lo}-{hi})")
    lo, hi = RSA["descriptions"]
    if not lo <= len(descriptions) <= hi:
        errs.append(f"{len(descriptions)} descriptions (allowed {lo}-{hi})")
    if len({h.lower() for h in headlines}) != len(headlines):
        errs.append("duplicate headlines")
    if len({d.lower() for d in descriptions}) != len(descriptions):
        errs.append("duplicate descriptions")
    if want_full and (len(headlines) < 15 or len(descriptions) < 4):
        errs.append(f"standard is 15 headlines and 4 descriptions (have {len(headlines)} and {len(descriptions)})")
    return errs


def check_assets(sitelinks=(), callouts=(), snippet_header: str | None = None, snippet_values=()) -> list[str]:
    """sitelinks: [(text, description1, description2)]."""
    errs = []
    for s in sitelinks:
        text, d1, d2 = (list(s) + ["", ""])[:3]
        if len(text) > ASSETS["sitelink_text"]:
            errs.append(f"sitelink text over 25: {text}")
        for d in (d1, d2):
            if d and len(d) > ASSETS["sitelink_description"]:
                errs.append(f"sitelink description over 35: {d}")
    for c in callouts:
        if len(c) > ASSETS["callout"]:
            errs.append(f"callout over 25: {c}")
    if snippet_header and snippet_header not in SNIPPET_HEADERS:
        errs.append(f"snippet header '{snippet_header}' is not one of the allowed headers")
    for v in snippet_values:
        if len(v) > ASSETS["snippet_value"]:
            errs.append(f"snippet value over 25: {v}")
    if snippet_values and len(snippet_values) < 3:
        errs.append("structured snippets need at least 3 values")
    return errs


def check_pmax(headlines, long_headlines, descriptions, business_name: str = "") -> list[str]:
    errs = []
    for kind, items, limit in (("headline", headlines, PMAX["headline"]),
                               ("long headline", long_headlines, PMAX["long_headline"]),
                               ("description", descriptions, PMAX["description"])):
        for t in items:
            if len(t) > limit:
                errs.append(f"{kind} over {limit} ({len(t)}): {t}")
    for kind, items, key in (("headlines", headlines, "headlines"), ("long headlines", long_headlines, "long_headlines"),
                             ("descriptions", descriptions, "descriptions")):
        lo, hi = PMAX[key]
        if not lo <= len(items) <= hi:
            errs.append(f"{len(items)} {kind} (allowed {lo}-{hi})")
    if descriptions and not any(len(d) <= PMAX["short_description"] for d in descriptions):
        errs.append("needs one description of 60 characters or fewer")
    if business_name and len(business_name) > ASSETS["business_name"]:
        errs.append("business name over 25")
    return errs
