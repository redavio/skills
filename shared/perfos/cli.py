"""Command line for the playbook math. Every command prints JSON.

    python3 -m perfos.cli <command> [options]

Commands (one per job; see each skill's SKILL.md for when to use which):
  gate          one item: clicks, conversions, cost vs goal -> cut / promote / flag / watch
  terms         a CSV of search terms (or any dimension) -> verdict per row, whole-week windows if dated
  diagnose      why a KPI moved: Shapley split of the gap across levers, plus the one-line driver
  mix           mix vs rate across segments for a ratio KPI
  targets       target CPA / ROAS backed out from LTV, CAC ratio and stage rates
  stage-values  dollar value per funnel stage from ACV and each stage's chance of winning
  first-target  first target near current, then steps toward the goal within the step limit
  ready         enough conversions to add a target?
  forecast      directional funnel forecast + starting budget split + spend scenarios
  rebalance     budget recommendation per campaign (needs daily data and impression share)
  pacing        spend vs pace for the period, and paced volume goals
  tracking      tracking-break check on daily clicks and conversions
  parity        Google vs Microsoft drift from two entity lists
  test-size     clicks per arm and weeks to the read date for an A/B test
  test-read     read a finished test at 95% confidence
  ice           rank test ideas by ICE; back-test finished ones
  expansion     ad groups that outgrew their campaign
  safety        safety level of a change and what it needs
  copy-check    RSA / asset / PMax copy against character and count limits
  fence         shared negative lists, ad-group exact fencing, negative checks
  audit-score   setup health % from checklist statuses
  name          parse or build a campaign name (channel|type|theme|geo|language)
  report        exec report table from daily facts (+ optional CRM leads)
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime

from . import alerts, audit, budget, expansion, experiments, fencing, gates, limits, naming, parity
from . import plan, prune_promote, report, safety, targets
from .diagnosis import deepdiver
from .schema import CrmRecord, FactRow


def _num(v, default=0.0):
    if v is None:
        return default
    s = str(v).strip().replace(",", "").replace("$", "").replace("%", "")
    if s in ("", "--", "-"):
        return default
    return float(s)


def _date(v):
    if v in (None, ""):
        return None
    if isinstance(v, date):
        return v
    return datetime.strptime(str(v)[:10], "%Y-%m-%d").date()


def _rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [{(k or "").strip().lower(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]


def _json(path_or_text):
    if path_or_text is None:
        return None
    s = str(path_or_text)
    if s.lstrip().startswith(("{", "[")):
        return json.loads(s)
    with open(s, encoding="utf-8") as f:
        return json.load(f)


def _out(obj):
    print(json.dumps(obj, indent=2, default=str))


def _goal_args(p):
    p.add_argument("--goal-cvr", type=float, help="goal conversion rate as a fraction (0.05 = 5%%)")
    p.add_argument("--target-cpa", type=float)
    p.add_argument("--target-roas", type=float, help="as a multiple (4 = 400%%)")
    p.add_argument("--value-per-conversion", type=float, help="for ROAS goals: average value per conversion")


# ---------- commands ----------

def c_gate(a):
    _out(gates.verdict(a.clicks, a.conversions, a.cost, a.goal_cvr, a.target_cpa, a.conversion_value,
                       a.target_roas, a.value_per_conversion) | {"clicks_line": gates.clicks_needed(a.conversions, a.goal_cvr)})


def c_terms(a):
    rows = _rows(a.csv)
    goals = _json(a.goals) if a.goals else None
    default = {"cvr": a.goal_cvr, "cpa": a.target_cpa, "roas": a.target_roas,
               "value_per_conversion": a.value_per_conversion}
    name_col = a.name_col
    dated = rows and "date" in rows[0]
    if dated:
        facts = []
        for r in rows:
            facts.append(FactRow(_date(r["date"]), "paid_search", r.get("platform", "google"), "",
                                 r.get("campaign", ""), r.get("campaign", ""), r.get("segment", "all") or "all",
                                 level=a.level, entity_id=r[name_col], entity_name=r[name_col],
                                 clicks=_num(r.get("clicks")), cost=_num(r.get("cost")),
                                 conversions=_num(r.get("conversions")),
                                 conversion_value=_num(r.get("conversion_value"))))
        segs = {f.segment for f in facts}
        g = goals or {s: default for s in segs}
        if any(s not in g for s in segs):
            sys.exit(f"No goal for segment(s): {sorted(segs - set(g))}. Ask for each segment's goal; never guess.")
        out = prune_promote.run(facts, g, a.max_weeks)
        _out({"windowed": True, "proposals": out,
              "watching": len({(f.campaign_id, f.entity_id) for f in facts}) - len(out)})
        return
    out = []
    for r in rows:
        seg = r.get("segment") or "all"
        g = (goals or {}).get(seg, default) if goals else default
        if g.get("cvr") is None:
            sys.exit(f"No goal conversion rate for segment '{seg}'. Ask the user; never guess.")
        v = gates.verdict(_num(r.get("clicks")), _num(r.get("conversions")), _num(r.get("cost")), g["cvr"],
                          g.get("cpa"), _num(r.get("conversion_value")), g.get("roas"), g.get("value_per_conversion"))
        out.append({"item": r.get(name_col), "campaign": r.get("campaign", ""), "segment": seg,
                    "clicks": _num(r.get("clicks")), "conversions": _num(r.get("conversions")),
                    "cost": _num(r.get("cost")), "verdict": v["action"], "act": v["act"], "reason": v["reason"]})
    order = {"cut": 0, "promote": 1, "flag": 2, "watch": 3}
    out.sort(key=lambda x: (order[x["verdict"]], -x["cost"]))
    _out({"windowed": False, "note": "No date column: treated as one window. Use whole weeks, 7 days minimum.",
          "rows": out})


def c_diagnose(a):
    actual, base = _json(a.actual), _json(a.base)
    from .metrics import derive
    actual, base = derive(actual), derive(base)
    mv = _json(a.min_volume) if a.min_volume else None
    chain = None
    if a.factors:
        chain = {"factors": [(f.split(":")[0], int(f.split(":")[1]) if ":" in f else 1) for f in a.factors.split(",")],
                 "higher_is_better": not a.lower_is_better}
    r = deepdiver.diagnose(a.kpi, actual, base, min_volume=mv, chain=chain, vs=a.vs)
    if r is None:
        sys.exit("Can't split: a lever is missing or zero where it's divided by. Check the inputs.")
    _out(r)


def c_mix(a):
    _out(deepdiver.mix_check(a.kpi, _json(a.actual), _json(a.base)))


def c_targets(a):
    _out(targets.recommend(a.ltv, a.ltv_to_cac, a.s2_to_won, a.conv_to_s2, a.pipeline_per_conversion,
                           a.media_share, _json(a.weekly_conversions) if a.weekly_conversions else None,
                           _json(a.weekly_s2s) if a.weekly_s2s else None))


def c_stage_values(a):
    _out(targets.stage_values(a.acv, _json(a.rates)))


def c_first_target(a):
    _out(targets.first_target(a.current, a.goal, a.step_limit, a.higher_is_better))


def c_ready(a):
    _out(targets.ready_for_target(a.conversions_30d, a.kind, a.platform))


def c_forecast(a):
    spec = _json(a.input)
    asm = plan.assumptions(spec.get("assumptions"))
    points = spec.get("points") or [{"name": "Conversion", "value": 0}]
    f = plan.forecast(spec.get("keywords", []), points, asm)
    has_comp = any(k.get("campaign_type") == "competitor" for k in spec.get("keywords", [])) or spec.get("has_competitors", False)
    overrides = {tuple(k.split(":")): v for k, v in (spec.get("daily_overrides") or {}).items()}
    out = {"forecast": f}
    if spec.get("monthly_budget"):
        out["split"] = plan.split(spec["monthly_budget"], asm, f["rows"], has_comp, overrides)
        out["scenarios"] = plan.scenarios(spec["monthly_budget"], asm, f["rows"], points, has_comp, spec.get("goals"))
    out["assumptions"] = asm
    out["note"] = "Directional guide, not a verdict. Volume never decides a keyword."
    _out(out)


def c_rebalance(a):
    spec = _json(a.input)
    end = _date(spec.get("period_end")) or max(_date(d) for c in spec["campaigns"] for d in c["daily"])
    recs, held = [], []
    for c in spec["campaigns"]:
        camp = budget.Campaign(str(c["campaign_id"]), c.get("name", ""), c.get("segment", "nonbrand"),
                               float(c["current_budget"]), float(c["target"]),
                               {_date(d): {k: float(v) for k, v in m.items()} for d, m in c["daily"].items()},
                               _date(c.get("last_change")), c.get("lost_is_budget"), c.get("impression_share"),
                               c.get("shared_budget", False), c.get("status", "enabled"))
        if camp.segment == "brand":
            held.append({"campaign": camp.name, **budget.brand_check(c.get("impression_share"))})
            continue
        r = budget.decide(camp, end, spec.get("config"))
        (recs if r else held).append(r or {"campaign": camp.name, "status": "no change"})
    _out({"recommendations": recs, "no_change": held,
          "note": "Recommendations only. A person approves each one; moves over the step limit need the client too."})


def c_pacing(a):
    today = _date(a.today) or date.today()
    out = alerts.pacing(a.spend, a.budget, today, a.tolerance, _date(a.start), _date(a.end))
    if a.goal is not None and a.actual is not None:
        share = alerts.share_of_period(today, _date(a.start), _date(a.end))
        out["goal"] = alerts.goal_pace(a.actual, a.goal, share, not a.lower_is_better)
    _out(out)


def c_tracking(a):
    rows = [(_date(r["date"]), _num(r["clicks"]), _num(r["conversions"])) for r in _rows(a.csv)]
    _out({"tracking_break": alerts.tracking_break(rows, a.quiet_days, a.min_clicks, a.before_days, a.min_before)})


def c_parity(a):
    drift = parity.check(_json(a.google), _json(a.microsoft))
    _out({"drift": drift, "clean": not drift})


def c_test_size(a):
    n = experiments.clicks_per_arm(a.baseline_cvr, a.min_lift, a.confidence, a.power)
    out = {"clicks_per_arm": n}
    if a.weekly_clicks:
        out["read_date_weeks"] = experiments.read_date_weeks(n, a.weekly_clicks, a.split)
    _out(out)


def c_test_read(a):
    _out(experiments.significance(a.control_conversions, a.control_clicks, a.test_conversions, a.test_clicks))


def c_ice(a):
    ideas = _json(a.input)
    ranked = experiments.rank(ideas)
    _out({"ranked": ranked, "backtest": experiments.backtest(ranked)})


def c_expansion(a):
    rows = [{"campaign": r["campaign"], "ad_group": r["ad_group"], "cost": _num(r["cost"]),
             "conversions": _num(r["conversions"])} for r in _rows(a.csv)]
    _out(expansion.outgrown(rows, a.min_share, a.min_conversions))


def c_safety(a):
    lvl = safety.level(a.kind, a.move_pct, safety.step_limit(a.step_limit))
    _out({"level": lvl, "needs": safety.needs(lvl), "missing": safety.problem(lvl, a.client_approval, a.revert_plan)})


def c_copy_check(a):
    spec = _json(a.input)
    out = {}
    for i, ad in enumerate(spec.get("rsas", [])):
        out[ad.get("ad_group", f"rsa_{i}")] = limits.check_rsa(ad["headlines"], ad["descriptions"],
                                                                ad.get("path1", ""), ad.get("path2", ""))
    if any(k in spec for k in ("sitelinks", "callouts", "snippet_values")):
        out["assets"] = limits.check_assets(spec.get("sitelinks", []), spec.get("callouts", []),
                                            spec.get("snippet_header"), spec.get("snippet_values", []))
    for i, g in enumerate(spec.get("asset_groups", [])):
        out[g.get("name", f"asset_group_{i}")] = limits.check_pmax(g.get("headlines", []), g.get("long_headlines", []),
                                                                   g.get("descriptions", []), g.get("business_name", ""))
    _out({"problems": out, "clean": not any(out.values())})


def c_fence(a):
    spec = _json(a.input)
    out = {"shared_lists": fencing.shared_lists(spec.get("brand_terms", []), spec.get("competitors", []),
                                                spec.get("junk"), spec.get("offered_free", False)),
           "login_support": fencing.login_support(spec.get("brand_terms", []), spec.get("competitors", []),
                                                  spec.get("competitor_churn_test", False)),
           "ad_group_fencing": {c: fencing.fence_ad_groups(g) for c, g in (spec.get("campaigns") or {}).items()},
           "competitor_match_types": {(c["name"] if isinstance(c, dict) else c):
                                      fencing.competitor_match_types(c["name"] if isinstance(c, dict) else c,
                                                                     bool(c.get("common_word")) if isinstance(c, dict) else False)
                                      for c in spec.get("competitors", [])}}
    all_negs = [n for lst in out["shared_lists"].values() for n in lst["negatives"]] + out["login_support"] \
        + [tuple(n) for n in spec.get("extra_negatives", [])]
    out["problems"] = fencing.check_negatives(all_negs, spec.get("protected_terms", []))
    _out(out)


def c_audit_score(a):
    spec = _json(a.input)
    res = audit.score(spec["items"], set(spec["channels_on"]) if spec.get("channels_on") is not None else None)
    if spec.get("findings"):
        res["findings"] = audit.rank_findings(spec["findings"])
    _out(res)


def c_name(a):
    if a.parse:
        _out({"parts": naming.parse(a.parse), "segment": naming.segment(a.parse)})
    else:
        parts = [a.channel, a.type, a.theme, a.geo, a.language]
        if any(p is None or "|" in p for p in parts):
            sys.exit("Give --channel --type --theme --geo --language; no '|' inside a value.")
        _out({"name": "|".join("_".join(p.strip().lower().split()) for p in parts)})


def c_report(a):
    facts = []
    for r in _rows(a.facts):
        seg = r.get("segment") or naming.segment(r.get("campaign", ""), r.get("channel_type")) or "unknown"
        facts.append(FactRow(_date(r["date"]), "paid_search", r.get("platform", "google"), r.get("account_id", ""),
                             r.get("campaign_id") or r.get("campaign", ""), r.get("campaign", ""), seg,
                             impressions=_num(r.get("impressions")), clicks=_num(r.get("clicks")),
                             cost=_num(r.get("cost")), conversions=_num(r.get("conversions")),
                             conversion_value=_num(r.get("conversion_value")),
                             eligible_impressions=(_num(r["impressions"]) / _num(r["impression_share"])
                                                   if r.get("impression_share") and _num(r.get("impression_share")) else None)))
    crm = []
    if a.crm:
        from . import matching
        for r in _rows(a.crm):
            crm.append(CrmRecord(r.get("lead_id", ""), _date(r.get("created")) or date.today(),
                                 platform=r.get("platform") or None, campaign_id=r.get("campaign_id") or None,
                                 mql_date=_date(r.get("mql_date")), sql_date=_date(r.get("sql_date")),
                                 s2_date=_date(r.get("s2_date")), won_date=_date(r.get("won_date")),
                                 pipeline_value=_num(r.get("pipeline_value")), won_value=_num(r.get("won_value")),
                                 match_method="crm"))
    start, end = _date(a.start), _date(a.end)
    rep = report.build(facts, crm, start, end, _json(a.goals) if a.goals else None, a.pace,
                       None, a.driver_kpi, a.columns.split(",") if a.columns else None)
    rep["tldr"] = report.tldr(rep)
    _out(rep)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="perfos", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("gate"); _goal_args(p)
    for x in ("clicks", "conversions", "cost"):
        p.add_argument(f"--{x}", type=float, required=True)
    p.add_argument("--conversion-value", type=float, default=0.0); p.set_defaults(f=c_gate)

    p = sp.add_parser("terms"); _goal_args(p)
    p.add_argument("--csv", required=True, help="columns: term (or --name-col), clicks, conversions, cost; optional date, campaign, segment, conversion_value")
    p.add_argument("--goals", help='JSON per segment: {"nonbrand": {"cvr": 0.04, "cpa": 250}, "brand": {...}}')
    p.add_argument("--name-col", default="term"); p.add_argument("--level", default="search_term")
    p.add_argument("--max-weeks", type=int, default=13); p.set_defaults(f=c_terms)

    p = sp.add_parser("diagnose")
    p.add_argument("--kpi", required=True, help="cpa, roas, conversions, cost_per_s2, pipeline_roas, s2s, pipeline, won_value ...")
    p.add_argument("--actual", required=True, help="JSON totals for the period (volumes; rates are derived)")
    p.add_argument("--base", required=True, help="JSON totals for goal or comparison period")
    p.add_argument("--vs", default="goal", choices=("goal", "prior"))
    p.add_argument("--min-volume", help='JSON e.g. {"clicks": 60, "conversions": 10}')
    p.add_argument("--factors", help="custom chain, e.g. cpc:1,cvr:-1"); p.add_argument("--lower-is-better", action="store_true")
    p.set_defaults(f=c_diagnose)

    p = sp.add_parser("mix"); p.add_argument("--kpi", required=True)
    p.add_argument("--actual", required=True); p.add_argument("--base", required=True); p.set_defaults(f=c_mix)

    p = sp.add_parser("targets")
    for x in ("ltv", "ltv-to-cac", "s2-to-won", "conv-to-s2"):
        p.add_argument(f"--{x}", type=float, required=True)
    p.add_argument("--pipeline-per-conversion", type=float); p.add_argument("--media-share", type=float, default=1.0)
    p.add_argument("--weekly-conversions"); p.add_argument("--weekly-s2s"); p.set_defaults(f=c_targets)

    p = sp.add_parser("stage-values"); p.add_argument("--acv", type=float, required=True)
    p.add_argument("--rates", required=True, help='JSON {stage: chance of winning from it}'); p.set_defaults(f=c_stage_values)

    p = sp.add_parser("first-target"); p.add_argument("--current", type=float, required=True)
    p.add_argument("--goal", type=float, required=True); p.add_argument("--step-limit", type=float, default=0.15)
    p.add_argument("--higher-is-better", action="store_true", help="ROAS"); p.set_defaults(f=c_first_target)

    p = sp.add_parser("ready"); p.add_argument("--conversions-30d", type=float, required=True)
    p.add_argument("--kind", choices=("tcpa", "troas"), default="tcpa")
    p.add_argument("--platform", choices=("google", "microsoft"), default="google"); p.set_defaults(f=c_ready)

    p = sp.add_parser("forecast"); p.add_argument("--input", required=True,
                                                  help="JSON: keywords, points, monthly_budget, assumptions, goals, daily_overrides")
    p.set_defaults(f=c_forecast)

    p = sp.add_parser("rebalance"); p.add_argument("--input", required=True, help="JSON: campaigns with daily data")
    p.set_defaults(f=c_rebalance)

    p = sp.add_parser("pacing")
    p.add_argument("--spend", type=float, required=True); p.add_argument("--budget", type=float, required=True)
    p.add_argument("--today"); p.add_argument("--start"); p.add_argument("--end")
    p.add_argument("--tolerance", type=float, default=15)
    p.add_argument("--actual", type=float, help="volume so far (conversions, value, pipeline)")
    p.add_argument("--goal", type=float, help="full-period goal for that volume")
    p.add_argument("--lower-is-better", action="store_true"); p.set_defaults(f=c_pacing)

    p = sp.add_parser("tracking"); p.add_argument("--csv", required=True, help="date, clicks, conversions")
    p.add_argument("--quiet-days", type=int, default=3); p.add_argument("--min-clicks", type=float, default=20)
    p.add_argument("--before-days", type=int, default=14); p.add_argument("--min-before", type=float, default=2)
    p.set_defaults(f=c_tracking)

    p = sp.add_parser("parity"); p.add_argument("--google", required=True); p.add_argument("--microsoft", required=True)
    p.set_defaults(f=c_parity)

    p = sp.add_parser("test-size"); p.add_argument("--baseline-cvr", type=float, required=True)
    p.add_argument("--min-lift", type=float, required=True, help="relative, 0.2 = 20%%")
    p.add_argument("--confidence", type=float, default=0.95, choices=(0.8, 0.9, 0.95, 0.99))
    p.add_argument("--power", type=float, default=0.80, choices=(0.8, 0.9, 0.95))
    p.add_argument("--weekly-clicks", type=float); p.add_argument("--split", type=float, default=0.5)
    p.set_defaults(f=c_test_size)

    p = sp.add_parser("test-read")
    for x in ("control-conversions", "control-clicks", "test-conversions", "test-clicks"):
        p.add_argument(f"--{x}", type=float, required=True)
    p.set_defaults(f=c_test_read)

    p = sp.add_parser("ice"); p.add_argument("--input", required=True,
                                             help="JSON list: {hypothesis, impact, confidence, ease, status?}")
    p.set_defaults(f=c_ice)

    p = sp.add_parser("expansion"); p.add_argument("--csv", required=True, help="campaign, ad_group, cost, conversions")
    p.add_argument("--min-share", type=float, default=0.5); p.add_argument("--min-conversions", type=float, default=30)
    p.set_defaults(f=c_expansion)

    p = sp.add_parser("safety"); p.add_argument("--kind", required=True)
    p.add_argument("--move-pct", type=float); p.add_argument("--step-limit")
    p.add_argument("--client-approval"); p.add_argument("--revert-plan"); p.set_defaults(f=c_safety)

    p = sp.add_parser("copy-check"); p.add_argument("--input", required=True,
                                                    help="JSON: rsas, sitelinks, callouts, snippet_header, snippet_values, asset_groups")
    p.set_defaults(f=c_copy_check)

    p = sp.add_parser("fence"); p.add_argument("--input", required=True,
                                               help="JSON: brand_terms, competitors, campaigns {campaign: {ad_group: [keywords]}}, protected_terms")
    p.set_defaults(f=c_fence)

    p = sp.add_parser("audit-score"); p.add_argument("--input", required=True,
                                                     help='JSON: {"items": {"A1": "pass", ...}, "channels_on": [...], "findings": [...]}')
    p.set_defaults(f=c_audit_score)

    p = sp.add_parser("name"); p.add_argument("--parse")
    for x in ("channel", "type", "theme", "geo", "language"):
        p.add_argument(f"--{x}")
    p.set_defaults(f=c_name)

    p = sp.add_parser("report"); p.add_argument("--facts", required=True,
                                                help="CSV: date, platform, campaign, campaign_id, impressions, clicks, cost, conversions, conversion_value, impression_share, segment")
    p.add_argument("--crm", help="CSV: lead_id, created, platform, campaign_id, mql_date, sql_date, s2_date, won_date, pipeline_value, won_value")
    p.add_argument("--start", required=True); p.add_argument("--end", required=True)
    p.add_argument("--goals", help="JSON {row_key: {metric: full-period goal}}"); p.add_argument("--pace", type=float, default=1.0)
    p.add_argument("--driver-kpi", default="cpa"); p.add_argument("--columns"); p.set_defaults(f=c_report)

    a = ap.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
