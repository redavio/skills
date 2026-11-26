"""LinkedIn Ads: the math and checks behind the linkedin-* skills. Standard library only.

The AI writes and judges; this code checks limits and does the math. Nothing here calls LinkedIn:
reads come from the Redavio connector (paid_linkedin_report, paid_linkedin_plan) or a Campaign Manager
export, and builds go through the Client Portal (Build > LinkedIn), paused.

Structure (shared/NAMING.md): campaigns linkedin|aware|target_accounts|us|en, linkedin|aware|icp|us|en,
linkedin|engaged|all|us|en; ad sets add the format (...|video).
"""
from __future__ import annotations

import difflib
import hashlib
import re
from urllib.parse import parse_qs, urlparse

from . import experiments, gates
from .naming import cmp

# Sponsored Content limits (LinkedIn's ad specs): text past the "see more" line still counts.
AD = {"intro": 600, "intro_visible": 150, "headline": 200, "headline_visible": 70, "url": 2000,
      "video_seconds": (3, 1800), "document_pages": 300}
CTAS = ("APPLY", "DOWNLOAD", "VIEW_QUOTE", "LEARN_MORE", "SIGN_UP", "SUBSCRIBE", "REGISTER", "JOIN", "ATTEND",
        "REQUEST_DEMO", "SEE_MORE")
MIN_AUDIENCE = 300          # LinkedIn won't serve below this
GOOD_AUDIENCE = 50_000      # below this, sponsored content delivers slowly
MIN_DAILY = 10.0            # LinkedIn's minimum daily budget per ad set (USD)
DEFAULT_CPM = 35.0
DEFAULT_CTR = 0.005
MAX_WEEKLY_FREQ = 3.0       # impressions per member per week before fatigue sets in
FATIGUE_DROP = 0.30         # CTR down this much from its first weeks = refresh the creative


def _n(v) -> float:
    s = str(v if v is not None else "").strip().replace(",", "").replace("$", "")
    if s in ("", "-", "--"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        raise ValueError(f"not a number: {v!r}") from None


# --- ad copy ---

def check_ad(ad: dict) -> dict:
    """One ad: errors block the build, warnings are where LinkedIn cuts text off on screen.
    ad: format (single_image, video, document, thought_leader), intro, headline, cta, landing_url,
    video_seconds?, document_pages?, campaign? (for the UTM check)."""
    errs, warns = [], []
    fmt = ad.get("format", "single_image")
    intro, head = ad.get("intro") or "", ad.get("headline") or ""
    if fmt != "thought_leader":
        if not intro:
            errs.append("intro text is missing")
        elif len(intro) > AD["intro"]:
            errs.append(f"intro text is {len(intro)} characters (max {AD['intro']})")
        elif len(intro) > AD["intro_visible"]:
            warns.append(f"intro text is {len(intro)} characters; LinkedIn shows about {AD['intro_visible']} before 'see more'")
        if fmt != "document":
            if not head:
                errs.append("headline is missing")
            elif len(head) > AD["headline"]:
                errs.append(f"headline is {len(head)} characters (max {AD['headline']})")
            elif len(head) > AD["headline_visible"]:
                warns.append(f"headline is {len(head)} characters; it's cut off after about {AD['headline_visible']}")
    cta = (ad.get("cta") or "LEARN_MORE").upper()
    if cta not in CTAS:
        errs.append(f"call to action {cta} isn't one of LinkedIn's: {', '.join(CTAS)}")
    url = ad.get("landing_url") or ""
    if fmt != "thought_leader":
        if not re.match(r"^https://", url):
            errs.append("landing_url must start with https://")
        else:
            errs += check_utms(url, ad.get("campaign"))
    if fmt == "video" and ad.get("video_seconds") is not None:
        lo, hi = AD["video_seconds"]
        if not lo <= float(ad["video_seconds"]) <= hi:
            errs.append(f"video is {ad['video_seconds']}s (LinkedIn takes {lo}s to {hi // 60} minutes)")
    if fmt == "document" and ad.get("document_pages") is not None and int(ad["document_pages"]) > AD["document_pages"]:
        errs.append(f"document has {ad['document_pages']} pages (max {AD['document_pages']})")
    return {"ad": ad.get("name") or head or intro[:40], "format": fmt, "errors": errs, "warnings": warns}


# --- tracking ---

def check_utms(url: str, campaign: str | None = None) -> list[str]:
    """The standard LinkedIn UTMs (shared/NAMING.md): source linkedin, medium paid_social, campaign = the slug."""
    q = {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}
    probs = []
    if q.get("utm_source") != "linkedin":
        probs.append(f"utm_source should be linkedin (is {q.get('utm_source') or 'missing'})")
    if q.get("utm_medium") != "paid_social":
        probs.append(f"utm_medium should be paid_social (is {q.get('utm_medium') or 'missing'})")
    want = cmp(campaign) if campaign else None
    if not q.get("utm_campaign"):
        probs.append("utm_campaign is missing")
    elif want and q["utm_campaign"] != want:
        probs.append(f"utm_campaign should be {want} (is {q['utm_campaign']})")
    if not q.get("utm_content"):
        probs.append("utm_content (the ad set format) is missing")
    return probs


def check_tracking(setup: dict) -> dict:
    """setup: insight_tag (partner id or ''), tag_on_site (bool), conversions [{name, enabled}],
    landing_urls [{campaign, url}]. Returns problems, each with the fix."""
    probs = []
    if not str(setup.get("insight_tag") or "").strip():
        probs.append("no Insight Tag: create one (Campaign Manager > Analyze > Insight Tag) and add it to the site")
    elif setup.get("tag_on_site") is False:
        probs.append("the Insight Tag isn't firing on the site: check it loads after advertising consent")
    convs = [c for c in setup.get("conversions") or [] if c.get("enabled", True)]
    if not convs:
        probs.append("no conversion: add one for the signup or demo request so the engaged campaign can optimize")
    for u in setup.get("landing_urls") or []:
        for p in check_utms(u.get("url", ""), u.get("campaign")):
            probs.append(f"{u.get('campaign') or u.get('url')}: {p}")
    return {"ok": not probs, "problems": probs, "conversions": [c.get("name") for c in convs]}


# --- target accounts ---

_SUFFIX = re.compile(r"[,.]?\s+(inc|llc|ltd|corp|corporation|co|gmbh|plc|limited)\.?$", re.I)


def clean_accounts(names: list[str]) -> dict:
    """Company names from Clay, G2, a CRM or Account Hub: trimmed, legal suffixes dropped, duplicates removed."""
    seen, out, dupes, changed = set(), [], [], []
    for raw in names:
        n = " ".join(str(raw).split())
        if not n:
            continue
        c = _SUFFIX.sub("", n).strip()
        if c != n:
            changed.append([n, c])
        if c.lower() in seen:
            dupes.append(c)
            continue
        seen.add(c.lower())
        out.append(c)
    return {"accounts": out, "count": len(out), "duplicates": dupes, "suffixes_removed": changed}


def check_matches(rows: list[dict], loose: float = 0.85) -> dict:
    """rows: [{company_name, matched_name|None}] as LinkedIn matched them. Flags misses and loose matches."""
    missing, fuzzy = [], []
    for r in rows:
        m = r.get("matched_name")
        if not m:
            missing.append(r["company_name"])
            continue
        score = difflib.SequenceMatcher(None, r["company_name"].lower(), m.lower()).ratio()
        if score < loose:
            fuzzy.append({"company": r["company_name"], "linkedin": m, "similarity": round(score, 2)})
    return {"found": len(rows) - len(missing), "total": len(rows), "missing": missing, "check": fuzzy}


# --- plan ---

def plan(campaigns: list[dict], cpm: float = DEFAULT_CPM, ctr: float = DEFAULT_CTR, days: int = 30) -> dict:
    """campaigns: [{name, members (audience size), ad_sets: [{name, daily_budget}]}]. A directional month per
    campaign: impressions, clicks, and impressions per member per week, with audience and budget checks."""
    if not campaigns:
        raise ValueError("no campaigns")
    out, problems = [], []
    for c in campaigns:
        daily = sum(_n(a.get("daily_budget")) for a in c.get("ad_sets") or [])
        for a in c.get("ad_sets") or []:
            if _n(a.get("daily_budget")) < MIN_DAILY:
                problems.append(f"{a.get('name')}: ${_n(a.get('daily_budget')):g}/day is under LinkedIn's ${MIN_DAILY:g} minimum")
        members = c.get("members")
        imps = daily * days / cpm * 1000
        freq = imps / members / (days / 7) if members else None
        if members is not None:
            if members < MIN_AUDIENCE:
                problems.append(f"{c['name']}: {members:,} members; LinkedIn needs {MIN_AUDIENCE} to serve. Widen it")
            elif members < GOOD_AUDIENCE:
                problems.append(f"{c['name']}: {members:,} members; under {GOOD_AUDIENCE:,} delivers slowly. "
                                "Add job titles or functions, or more target accounts")
            if freq and freq > MAX_WEEKLY_FREQ:
                fit = daily * MAX_WEEKLY_FREQ / freq
                floor = MIN_DAILY * len(c.get("ad_sets") or [1])
                fix = (f"Lower the budget to ${fit:.0f}/day or widen it" if fit >= floor else
                       f"The ${floor:g}/day minimum for its ad sets is still too much: widen the audience "
                       f"(more accounts or titles), or run one ad set instead of {len(c.get('ad_sets') or [])}")
                problems.append(f"{c['name']}: about {freq:.1f} impressions per member a week; over {MAX_WEEKLY_FREQ:g} "
                                f"wears the audience out. {fix}")
        out.append({"campaign": c["name"], "members": members, "daily_budget": round(daily, 2),
                    "monthly_budget": round(daily * days, 2), "impressions": round(imps), "clicks": round(imps * ctr),
                    "weekly_frequency": round(freq, 2) if freq else None})
    return {"campaigns": out, "monthly_total": round(sum(c["monthly_budget"] for c in out), 2), "problems": problems,
            "assumptions": {"cpm": cpm, "ctr": ctr},
            "note": "Directional: replace the CPM and CTR with your own after 2-4 weeks."}


# --- weekly review ---

def weekly(rows: list[dict], audiences: list[dict] | None = None, target_cpa: float | None = None) -> dict:
    """rows: week, campaign, ad_set, format, impressions, clicks, spend, conversions (paid_linkedin_report or a
    Campaign Manager export). Awareness ad sets are judged on cost to reach (CPM), frequency and creative fatigue;
    the engaged campaign on conversions through the volume gate."""
    if not rows:
        return {"empty": True, "message": "No rows: nothing has run yet. Come back after 2 full weeks live."}
    for col in ("ad_set", "impressions", "clicks", "spend"):
        if col not in rows[0]:
            raise ValueError(f"missing column {col} (need week, campaign, ad_set, format, impressions, clicks, spend, conversions)")
    members = {a["campaign"]: a.get("members") for a in audiences or []}
    sets: dict[str, dict] = {}
    for r in rows:
        s = sets.setdefault(r["ad_set"], {"ad_set": r["ad_set"], "campaign": r.get("campaign") or r["ad_set"].rsplit("|", 1)[0],
                                          "format": r.get("format") or r["ad_set"].rsplit("|", 1)[-1], "weeks": {}})
        w = s["weeks"].setdefault(r.get("week", ""), {"impressions": 0.0, "clicks": 0.0, "spend": 0.0, "conversions": 0.0})
        for c in w:
            w[c] += _n(r.get(c))
    tot = {c: sum(w[c] for s in sets.values() for w in s["weeks"].values()) for c in ("impressions", "clicks", "spend", "conversions")}
    acct_cpm = tot["spend"] / tot["impressions"] * 1000 if tot["impressions"] else None
    # Conversions are judged inside the engaged campaign only: awareness spend isn't meant to convert.
    eng = [w for s in sets.values() if "|engaged|" in f"|{s['campaign']}|" for w in s["weeks"].values()]
    e = {c: sum(w[c] for w in eng) for c in ("clicks", "spend", "conversions")}
    acct_cpa = e["spend"] / e["conversions"] if e["conversions"] else None
    acct_cvr = e["conversions"] / e["clicks"] if e["clicks"] else 0.0
    out = []
    for s in sets.values():
        weeks = [s["weeks"][k] for k in sorted(s["weeks"])]
        t = {c: sum(w[c] for w in weeks) for c in ("impressions", "clicks", "spend", "conversions")}
        cpm = t["spend"] / t["impressions"] * 1000 if t["impressions"] else None
        ctr = t["clicks"] / t["impressions"] if t["impressions"] else None
        m = members.get(s["campaign"])
        freq = weeks[-1]["impressions"] / m if m else None
        first = weeks[:2]
        f_imps = sum(w["impressions"] for w in first)
        f_ctr = sum(w["clicks"] for w in first) / f_imps if f_imps else None
        l_ctr = weeks[-1]["clicks"] / weeks[-1]["impressions"] if weeks[-1]["impressions"] else None
        engaged = "|engaged|" in f"|{s['campaign']}|"
        if engaged and acct_cvr > 0:
            v = gates.verdict(t["clicks"], t["conversions"], t["spend"], acct_cvr, target_cpa or acct_cpa)
            action, reason = {"promote": "scale"}.get(v["action"], v["action"]), v["reason"]
        elif len(weeks) >= 3 and f_ctr and l_ctr is not None and weeks[-1]["impressions"] >= 1000 and l_ctr < f_ctr * (1 - FATIGUE_DROP):
            action, reason = "refresh", f"CTR fell from {f_ctr:.2%} to {l_ctr:.2%}: the audience has seen this creative"
        elif freq and freq > MAX_WEEKLY_FREQ:
            action, reason = "flag", f"{freq:.1f} impressions per member last week (over {MAX_WEEKLY_FREQ:g}): lower its budget"
        elif cpm and acct_cpm and t["impressions"] >= 5000 and cpm > acct_cpm * 1.5:
            action, reason = "flag", f"${cpm:.0f} CPM is 1.5x the account's ${acct_cpm:.0f}: check targeting overlap and the bid"
        elif t["impressions"] < 5000:
            action, reason = "watch", "under 5,000 impressions: not enough to call"
        else:
            action, reason = "keep", "cost to reach and CTR in line with the account"
        out.append({"ad_set": s["ad_set"], "campaign": s["campaign"], "format": s["format"], "weeks": len(weeks),
                    **{k: round(v, 2) for k, v in t.items()}, "cpm": round(cpm, 2) if cpm else None,
                    "ctr": round(ctr, 4) if ctr is not None else None,
                    "weekly_frequency": round(freq, 2) if freq else None, "action": action, "reason": reason})
    order = {"cut": 0, "refresh": 1, "flag": 2, "scale": 3, "keep": 4, "watch": 5}
    out.sort(key=lambda a: (order[a["action"]], -a["spend"]))
    return {"empty": False, "account": {**{k: round(v, 2) for k, v in tot.items()},
                                        "cpm": round(acct_cpm, 2) if acct_cpm else None, "engaged_cpa": acct_cpa},
            "ad_sets": out}


# --- holdout test at the account level ---

def holdout_split(accounts: list[str], holdout_share: float = 0.5, salt: str = "linkedin") -> dict:
    """A fixed, repeatable split of target accounts: the holdout is excluded from every LinkedIn campaign
    for the test. Same list + salt = same split, so it can be re-made any time."""
    if not 0.1 <= holdout_share <= 0.5:
        raise ValueError("holdout_share should be between 0.1 and 0.5")
    clean = clean_accounts(accounts)["accounts"]
    h = lambda a: int(hashlib.sha256(f"{salt}|{a.lower()}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    holdout = sorted(a for a in clean if h(a) < holdout_share)
    test = sorted(a for a in clean if h(a) >= holdout_share)
    return {"test": test, "holdout": holdout, "counts": {"test": len(test), "holdout": len(holdout)},
            "how": "Add the holdout companies as an exclusion on every LinkedIn campaign for 8-12 weeks, then read "
                   "pipeline in both groups with linkedin-measure."}


# --- measure: pipeline at accounts reached vs not ---

def measure(accounts: list[dict], min_impressions: int = 1) -> dict:
    """accounts: [{account, impressions, opportunities, pipeline}] over the same 90 days (CRM + LinkedIn's
    company report, or a holdout test's two groups). Compares accounts LinkedIn reached with ones it didn't."""
    if not accounts:
        raise ValueError("no accounts")
    groups = {"reached": [], "not_reached": []}
    for a in accounts:
        groups["reached" if _n(a.get("impressions")) >= min_impressions else "not_reached"].append(a)
    out = {}
    for k, g in groups.items():
        n = len(g)
        opps = sum(1 for a in g if _n(a.get("opportunities")) > 0)
        pipe = sum(_n(a.get("pipeline")) for a in g)
        out[k] = {"accounts": n, "with_opportunity": opps, "opportunity_rate": opps / n if n else None,
                  "pipeline": round(pipe, 2), "pipeline_per_account": round(pipe / n, 2) if n else None}
    r, nr = out["reached"], out["not_reached"]
    lift = (r["opportunity_rate"] / nr["opportunity_rate"] - 1) if r["opportunity_rate"] and nr["opportunity_rate"] else None
    sig = (experiments.significance(nr["with_opportunity"], nr["accounts"], r["with_opportunity"], r["accounts"])
           if r["accounts"] and nr["accounts"] else None)
    return {**out, "opportunity_lift": round(lift, 3) if lift is not None else None, "significance": sig,
            "note": "Reached accounts can differ from the rest (bigger, already warmer). A holdout split "
                    "(linkedin-test) is the clean read; this is the everyday one."}
