"""ChatGPT ads: the math and checks behind the chatgpt-* skills. Standard library only.

Limits and API shapes are OpenAI's Ads docs (https://developers.openai.com/ads/llms.txt), read 2026-11-21.
The AI writes and judges; this code checks limits, does the math and builds the request. Nothing here
calls OpenAI: reading reports lives in ads_scripts/_chatgpt.py (GET only), and nothing ever writes.
"""
from __future__ import annotations

import hashlib
import re

from . import gates, targets

CARD = {"title": (3, 50), "body": 100, "url": 2048, "image_min_px": 640, "multi_images": (4, 6)}
HINTS_PER_GROUP = 2000
OBJECTIVES = ("impressions", "clicks", "conversions")
DEFAULT_CPM = 60.0
MICROS = 1_000_000


# --- ad copy ---

def check_card(card: dict) -> list[str]:
    """Problems with one chat card ad. images (optional): [{width, height}]; 2+ images = a multi-image card."""
    errs = []
    title, body, url = card.get("title"), card.get("body"), card.get("target_url")
    lo, hi = CARD["title"]
    if not title:
        errs.append("title is missing")
    elif not lo <= len(title) <= hi:
        errs.append(f"title is {len(title)} characters (allowed {lo}-{hi}): {title}")
    if not body:
        errs.append("body is missing")
    elif len(body) > CARD["body"]:
        errs.append(f"body is {len(body)} characters (max {CARD['body']}): {body}")
    if not url:
        errs.append("target_url is missing")
    elif not re.match(r"^https?://", url):
        errs.append(f"target_url must start with http:// or https://: {url}")
    elif len(url) > CARD["url"]:
        errs.append(f"target_url is {len(url)} characters (max {CARD['url']})")
    images = card.get("images") or []
    px = CARD["image_min_px"]
    for im in images:
        w, h = int(im.get("width", 0)), int(im.get("height", 0))
        if w < px or h < px:
            errs.append(f"image {w}x{h} is under the {px}x{px} minimum")
    if len(images) > 1:
        lo, hi = CARD["multi_images"]
        if not lo <= len(images) <= hi:
            errs.append(f"a multi-image card needs {lo}-{hi} images (has {len(images)})")
        if any(int(im.get("width", 0)) != int(im.get("height", 0)) for im in images):
            errs.append("every image in a multi-image card must be square (1:1)")
    return errs


# --- context hints ---

_MATCH = re.compile(r'^\s*(\[.*\]|".*"|\+.*)\s*$')


def check_hints(groups: list[dict]) -> dict:
    """Context hints per ad group: [{ad_group, cluster, hints: [...]}]. Hints are not keywords: OpenAI
    ignores match types, so brackets, quotes and + are stripped and noted. Every group needs a cluster
    (the topic name shared with paid search, SEO and AEO). Returns cleaned hints and problems per group."""
    out, ok = [], True
    for g in groups:
        probs, clean, seen = [], [], set()
        name = g.get("ad_group") or g.get("name") or ""
        if not (g.get("cluster") or "").strip():
            probs.append("no cluster: give every ad group the topic cluster it shares with paid search, SEO and AEO")
        stripped = empty = dupes = 0
        for h in g.get("hints") or []:
            h = str(h)
            if _MATCH.match(h):
                stripped += 1
                h = h.strip().strip("[]\"").lstrip("+")
            h = " ".join(h.split())
            if not h:
                empty += 1
                continue
            if h.lower() in seen:
                dupes += 1
                continue
            seen.add(h.lower())
            clean.append(h)
        if stripped:
            probs.append(f"{stripped} hint(s) used match type syntax; hints aren't keywords, so it was removed")
        if dupes:
            probs.append(f"{dupes} duplicate hint(s) removed")
        if empty:
            probs.append(f"{empty} empty hint(s) removed")
        if len(clean) > HINTS_PER_GROUP:
            probs.append(f"{len(clean):,} hints; the limit is {HINTS_PER_GROUP:,} per ad group")
        if not clean:
            probs.append("no hints")
        blocking = [p for p in probs if p.startswith(("no cluster", "no hints")) or "limit" in p]
        ok = ok and not blocking
        out.append({"ad_group": name, "cluster": g.get("cluster", ""), "hints": clean, "count": len(clean),
                    "problems": probs})
    return {"ok": ok, "groups": out}


# --- plan ---

def _rate(v, name):
    if v is None or not 0 < float(v) <= 1:
        raise ValueError(f"{name} must be a rate between 0 and 1 (0.007 = 0.7%), got {v}")
    return float(v)


def plan(monthly_budget: float, objective: str, ctr: float, cvr: float, cpm: float | None = DEFAULT_CPM,
         cpc: float | None = None, conversions_30d: float = 0, days: int = 30) -> dict:
    """Directional month: impressions, clicks, conversions and CPA from a budget and rate assumptions.
    Bids are per impression for impressions campaigns ($60 CPM = 60000 micros) and per click otherwise.
    Conversion bidding waits for the same 30-conversions-in-30-days line as search; until then, clicks."""
    if not monthly_budget or monthly_budget <= 0:
        raise ValueError("monthly budget must be more than 0")
    if objective not in OBJECTIVES:
        raise ValueError(f"objective must be one of {', '.join(OBJECTIVES)} (got {objective})")
    ctr, cvr = _rate(ctr, "ctr"), _rate(cvr, "cvr")
    if not cpm and not cpc:
        raise ValueError("give a cpm or cpc assumption (e.g. cpm 60 or cpc 2.50)")
    if cpc:
        clicks = monthly_budget / cpc
        impressions = clicks / ctr
    else:
        impressions = monthly_budget / cpm * 1000
        clicks = impressions * ctr
    conversions = clicks * cvr
    gate = targets.ready_for_target(conversions_30d)
    final = objective
    if objective == "conversions":
        if gate["ready"]:
            reason = f"{conversions_30d:g} conversions in 30 days, past the {gate['need']} needed"
        else:
            final = "clicks"
            reason = (f"{conversions_30d:g} conversions in 30 days; conversion bidding needs {gate['need']}. "
                      "Start on clicks and switch when it gets there")
    else:
        reason = "not asked for"
    if final == "impressions":
        bid = (cpm or monthly_budget / impressions * 1000) / 1000
    else:
        bid = cpc or monthly_budget / clicks
    return {"objective": final, "monthly_budget": monthly_budget, "daily_budget": round(monthly_budget / days, 2),
            "impressions": round(impressions), "clicks": round(clicks), "conversions": round(conversions, 2),
            "cpa": monthly_budget / conversions if conversions else None,
            "max_bid_micros": round(bid * MICROS),
            "conversion_bidding": {"ready": gate["ready"], "have": conversions_30d, "need": gate["need"], "reason": reason},
            "assumptions": {"cpm": cpm if not cpc else None, "cpc": cpc, "ctr": ctr, "cvr": cvr},
            "note": "Directional. ChatGPT ads are new: replace these assumptions with your own numbers after 2-4 weeks."}


# --- weekly review ---

NEED = ("ad_group", "clicks", "spend", "conversions")


def _n(row, col, i):
    v = row.get(col)
    s = str(v if v is not None else "").strip().replace(",", "").replace("$", "")
    if s in ("", "-", "--"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        raise ValueError(f"{col} isn't a number in row {i}: {v!r}") from None


def weekly(rows: list[dict], ads: list[dict] | None = None, target_cpa: float | None = None,
           goal_cvr: float | None = None) -> dict:
    """Ad groups through the volume gate against the account (or your target), plus every ad's copy checked.

    rows: week, campaign, ad_group, cluster, impressions, clicks, spend, conversions (an insights export
    or ads_scripts/chatgpt_report.py). The goal conversion rate and CPA default to the account's own, so a
    group is cut only when it's 95% surely worse than the rest. Broad hints are the usual cause."""
    if not rows:
        return {"empty": True, "message": "No rows: export at least 2 full weeks of ad group insights."}
    missing = [c for c in NEED if c not in rows[0]]
    if missing:
        raise ValueError(f"missing column(s): {', '.join(missing)} (need week, ad_group, cluster, impressions, "
                         "clicks, spend, conversions)")
    agg: dict[str, dict] = {}
    for i, r in enumerate(rows, 1):
        g = agg.setdefault(r["ad_group"], {"ad_group": r["ad_group"], "campaign": r.get("campaign", ""),
                                           "cluster": r.get("cluster", ""), "impressions": 0.0, "clicks": 0.0,
                                           "spend": 0.0, "conversions": 0.0, "weeks": set()})
        for c in ("impressions", "clicks", "spend", "conversions"):
            g[c] += _n(r, c, i)
        g["weeks"].add(r.get("week") or r.get("date") or "")
    tot = {c: sum(g[c] for g in agg.values()) for c in ("impressions", "clicks", "spend", "conversions")}
    acct_cpa = tot["spend"] / tot["conversions"] if tot["conversions"] else None
    acct_cvr = tot["conversions"] / tot["clicks"] if tot["clicks"] else 0.0
    goal = goal_cvr or acct_cvr
    bench = target_cpa or acct_cpa
    out = []
    for g in agg.values():
        cpa = g["spend"] / g["conversions"] if g["conversions"] else None
        if goal > 0:
            v = gates.verdict(g["clicks"], g["conversions"], g["spend"], goal, bench)
        else:
            v = {"action": "watch", "reason": "no conversions in the account yet"}
        action = {"promote": "scale"}.get(v["action"], v["action"])
        out.append({"ad_group": g["ad_group"], "campaign": g["campaign"], "cluster": g["cluster"],
                    "weeks": len(g["weeks"]), "impressions": g["impressions"], "clicks": g["clicks"],
                    "spend": round(g["spend"], 2), "conversions": g["conversions"],
                    "ctr": g["clicks"] / g["impressions"] if g["impressions"] else None,
                    "cpc": g["spend"] / g["clicks"] if g["clicks"] else None, "cpa": cpa,
                    "cpa_vs_account": cpa / acct_cpa if cpa and acct_cpa else None,
                    "action": action, "reason": v["reason"],
                    "next": {"cut": "narrow or cut its context hints, or pause the ad group",
                             "flag": "watch: spend with no conversions, below the click line",
                             "scale": "beating the account: room for more budget or bid",
                             "watch": "not enough data to call"}[action]})
    order = {"cut": 0, "flag": 1, "scale": 2, "watch": 3}
    out.sort(key=lambda g: (order[g["action"]], -g["spend"]))
    ad_problems = []
    for a in ads or []:
        p = check_card(a)
        if p:
            ad_problems.append({"ad": a.get("ad") or a.get("name") or a.get("title"), "ad_group": a.get("ad_group", ""),
                                "problems": p})
    return {"empty": False,
            "account": {**{k: round(v, 2) for k, v in tot.items()}, "cpa": acct_cpa, "cvr": acct_cvr,
                        "goal_cvr": goal, "benchmark_cpa": bench,
                        "benchmark": "your target CPA" if target_cpa else "the account's own CPA"},
            "ad_groups": out, "ad_problems": ad_problems}


# --- build: one bulk mutation job, paused, dry run ---

def _key(*parts) -> str:
    return "rdv-" + hashlib.sha256("|".join(parts).encode()).hexdigest()[:20]


def bulk_job(build: dict) -> dict:
    """The body for POST /bulk_mutation_jobs: campaign, ad groups and ads, all PAUSED, validate_only on.
    build: {campaign: {name, objective, daily_budget | lifetime_budget, countries}, ad_groups: [{name, cluster,
    max_cpc | max_cpm, hints, ads: [{name, title, body, target_url, image_url}]}]}. Refuses anything that
    would bounce. Nothing is sent: the person sends it themselves (or builds it in Ads Manager) after review."""
    c = build.get("campaign") or {}
    if not c.get("name"):
        raise ValueError("campaign needs a name")
    if c.get("objective", "clicks") not in OBJECTIVES:
        raise ValueError(f"objective must be one of {', '.join(OBJECTIVES)}")
    daily, life = c.get("daily_budget"), c.get("lifetime_budget")
    if bool(daily) == bool(life):
        raise ValueError("give exactly one of daily_budget or lifetime_budget")
    groups = build.get("ad_groups") or []
    if not groups:
        raise ValueError("no ad groups")
    hints = check_hints([{"ad_group": g.get("name"), "cluster": g.get("cluster"), "hints": g.get("hints")} for g in groups])
    errs = [f"{h['ad_group']}: {p}" for h in hints["groups"] for p in h["problems"]
            if p.startswith(("no cluster", "no hints")) or "limit" in p]
    for g in groups:
        for a in g.get("ads") or []:
            errs += [f"{g.get('name')} / {a.get('name')}: {p}" for p in check_card(a)]
            if not re.match(r"^https://", a.get("image_url") or ""):
                errs.append(f"{g.get('name')} / {a.get('name')}: image_url must be a public https:// address")
        if not g.get("ads"):
            errs.append(f"{g.get('name')}: no ads")
        if not (g.get("max_cpc") or g.get("max_cpm")):
            errs.append(f"{g.get('name')}: give max_cpc (clicks, conversions) or max_cpm (impressions)")
    if errs:
        raise ValueError("fix before building:\n- " + "\n- ".join(errs))
    ck = _key(c["name"])
    ops = [{"operation_id": "op-1", "type": "campaign.create", "idempotency_key": ck,
            "input": {"name": c["name"], "status": "paused", "budget_type": "daily" if daily else "lifetime",
                      "max_budget_micros": round((daily or life) * MICROS),
                      "billing_event_type": "impression" if c.get("objective") == "impressions" else "click",
                      "target_countries": c.get("countries") or []}}]
    clusters = {}
    for g, h in zip(groups, hints["groups"]):
        gk = _key(c["name"], g["name"])
        bid = {"max_bid_micros": round(g["max_cpc"] * MICROS)} if g.get("max_cpc") else \
              {"max_cpm_bid_micros": round(g["max_cpm"] * MICROS)}
        ops.append({"operation_id": f"op-{len(ops) + 1}", "type": "ad_group.create", "idempotency_key": gk,
                    "input": {"campaign_idempotency_key": ck, "name": g["name"], "status": "paused",
                              "context_hints": h["hints"], **bid}})
        clusters[g["name"]] = g["cluster"]
        for a in g["ads"]:
            ops.append({"operation_id": f"op-{len(ops) + 1}", "type": "ad.create",
                        "idempotency_key": _key(c["name"], g["name"], a.get("name") or a["title"]),
                        "input": {"campaign_idempotency_key": ck, "ad_group_idempotency_key": gk,
                                  "name": a.get("name") or a["title"], "status": "paused", "title": a["title"],
                                  "body": a["body"], "target_url": a["target_url"], "source_image_url": a["image_url"]}})
    if len(ops) > 1000:
        raise ValueError(f"{len(ops)} operations; one job takes 1,000. Split the build.")
    return {"validate_only": True, "partial_failure": False, "operations": ops, "clusters": clusters,
            "note": "Everything is paused. Send with validate_only true first; set it false only after the person says yes."}


# --- measure: ChatGPT next to the other channels ---

def compare(channels: list[dict]) -> dict:
    """channels: [{channel, spend, conversions, pipeline?, click_window_days?, view_window_days?}].
    Ranks on cost per pipeline dollar when every channel has pipeline, else on CPA, and warns when the
    channels count conversions differently (ChatGPT defaults to 30-day click + 1-day view)."""
    if not channels:
        raise ValueError("no channels to compare")
    warnings, out = [], []
    for ch in channels:
        spend, conv, pipe = float(ch.get("spend") or 0), float(ch.get("conversions") or 0), ch.get("pipeline")
        out.append({"channel": ch.get("channel", ""), "spend": spend, "conversions": conv,
                    "cpa": spend / conv if conv else None,
                    "pipeline": float(pipe) if pipe is not None else None,
                    "cost_per_pipeline_dollar": spend / float(pipe) if pipe else None,
                    "click_window_days": ch.get("click_window_days"), "view_window_days": ch.get("view_window_days")})
    if all(c["pipeline"] for c in out):
        out.sort(key=lambda c: c["cost_per_pipeline_dollar"])
        basis = "cost per pipeline dollar"
    else:
        out.sort(key=lambda c: (c["cpa"] is None, c["cpa"] or 0))
        basis = "CPA"
        warnings.append("ranked on CPA: add pipeline from your CRM for every channel to rank on what matters")
    clicks = {c["click_window_days"] for c in out if c["click_window_days"] is not None}
    views = {c["view_window_days"] or 0 for c in out if c["view_window_days"] is not None}
    if len(clicks) > 1:
        warnings.append(f"click windows differ ({sorted(clicks)} days): set ChatGPT's attribution_window_days to match")
    if len(views) > 1:
        warnings.append("view-through counting differs: compare with view_through_attribution_window_days=0, "
                        "since OpenAI bills and optimizes on clicks only")
    return {"basis": basis, "channels": out, "warnings": warnings}
