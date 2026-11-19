"""Negatives and fencing (performance-os standards/targeting.md, context/build.md A4).

- Shared lists: brand terms negative in Non-brand and Competitor; competitor names negative in
  Brand and Non-brand; a junk list everywhere. Phrase by default, never broad.
- Inside a campaign, each ad group carries the other ad groups' keywords as EXACT negatives so a
  search lands in the ad group built for it.
- Plurals added (negatives don't match close variants). Real product terms are never negated.
"""
from __future__ import annotations

JUNK_STARTER = ["jobs", "job", "careers", "career", "salary", "salaries", "hiring", "internship",
                "course", "courses", "certification", "tutorial", "template", "templates",
                "free download", "crack", "torrent", "reddit"]
LOGIN_SUPPORT = ["login", "log in", "sign in", "support", "customer service", "phone number",
                 "help center", "status", "outage", "cancel", "refund"]


def plural(term: str) -> str | None:
    t = term.strip().lower()
    if not t or t.endswith("s"):
        return None
    if t.endswith("y") and len(t) > 1 and t[-2] not in "aeiou":
        return t[:-1] + "ies"
    if t.endswith(("ch", "sh", "x", "z")):
        return t + "es"
    return t + "s"


def with_plurals(terms) -> list[str]:
    out = []
    for t in terms:
        for x in (t.strip().lower(), plural(t)):
            if x and x not in out:
                out.append(x)
    return out


def shared_lists(brand_terms, competitors, junk=None, offered_free: bool = False) -> dict:
    """Return the three shared negative lists as [(text, match)] plus where each attaches.
    competitors: names (strings) or {"name", "common_word"}."""
    names = [c["name"] if isinstance(c, dict) else c for c in competitors]
    junk = list(junk if junk is not None else JUNK_STARTER)
    if not offered_free and "free" not in junk:
        junk.append("free")
    return {
        "brand_terms": {"attach_to": ["nonbrand", "competitor", "pmax"],
                        "negatives": [(t, "PHRASE") for t in with_plurals(brand_terms)]},
        "competitors": {"attach_to": ["brand", "nonbrand"],
                        "negatives": [(t, "PHRASE") for t in with_plurals(names)]},
        "junk": {"attach_to": ["brand", "nonbrand", "competitor"],
                 "negatives": [(t, "PHRASE") for t in with_plurals(junk)]},
    }


def login_support(brand_terms, competitors=(), competitor_churn_test: bool = False) -> list[tuple]:
    """Own-brand login/support as phrase negatives (Brand campaign); competitor login/support too,
    unless a churn test is running."""
    out = [(f"{b} {w}", "PHRASE") for b in brand_terms for w in LOGIN_SUPPORT]
    if not competitor_churn_test:
        names = [c["name"] if isinstance(c, dict) else c for c in competitors]
        out += [(f"{n} {w}", "PHRASE") for n in names for w in LOGIN_SUPPORT]
    return out


def fence_ad_groups(ad_groups: dict) -> dict:
    """ad_groups: {ad_group: [keyword text]} for ONE campaign. Returns {ad_group: [(text, 'EXACT')]}:
    every other ad group's keywords, skipping any that are also this group's own keyword."""
    own = {g: {k.strip().lower() for k in kws} for g, kws in ad_groups.items()}
    out = {}
    for g in ad_groups:
        negs = []
        for other, kws in own.items():
            if other == g:
                continue
            for k in sorted(kws):
                if k not in own[g] and (k, "EXACT") not in negs:
                    negs.append((k, "EXACT"))
        out[g] = negs
    return out


def competitor_match_types(name: str, common_word: bool) -> list[str]:
    """Common-word competitor names (e.g. a name that is also a dictionary word) go phrase and exact only."""
    return ["PHRASE", "EXACT"] if common_word else ["BROAD", "PHRASE", "EXACT"]


def check_negatives(negatives: list[tuple], protected_terms=()) -> list[str]:
    """Problems: broad negatives, and negatives that block a real product term."""
    errs = []
    prot = [p.strip().lower() for p in protected_terms]
    for text, match in negatives:
        m = match.upper()
        if m == "BROAD":
            errs.append(f"broad negative not allowed: {text}")
        t = " ".join(text.strip().lower().split())
        for p in prot:
            blocks = (t == p) if m == "EXACT" else (f" {t} " in f" {p} ")
            if blocks:
                errs.append(f"negative '{text}' ({m.lower()}) would block product term '{p}'")
    return errs
