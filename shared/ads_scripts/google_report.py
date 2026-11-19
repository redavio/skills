"""Pull a Google Ads report to CSV in the shape the perfos commands read. Read only.

  python3 google_report.py campaign_daily --days 28 --out campaigns.csv
  python3 google_report.py search_terms --days 28 [--daily] --out terms.csv
  python3 google_report.py keywords | ad_groups | landing_pages | expanded_landing_pages
  python3 google_report.py by --dimension device|hour|day_of_week|network
  python3 google_report.py pmax_networks
  python3 google_report.py pmax_search_terms --campaign-id 123
  python3 google_report.py change_history --days 28
  python3 google_report.py gaql --query "SELECT ..."      (anything else)

Data runs through yesterday. Cost is in account currency (micros converted). The segment column
(brand / nonbrand / competitor / pmax) is read from campaign names that follow
channel|type|theme|geo|language; anything else is 'unknown' and must be tagged by a person.
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _google as G  # noqa: E402


def _naming():
    for p in (Path(__file__).resolve().parents[1], Path(__file__).resolve().parent.parent):
        if (p / "perfos").is_dir():
            sys.path.insert(0, str(p))
    try:
        from perfos import naming
        return naming
    except ImportError:
        return None


NAMING = _naming()


def seg(name, channel_type=""):
    if NAMING is None:
        return ""
    return NAMING.segment(name, channel_type) or "unknown"


M = "metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.conversions_value"


def base(r):
    m = r.metrics
    return {"impressions": m.impressions, "clicks": m.clicks, "cost": round(m.cost_micros / 1e6, 2),
            "conversions": round(m.conversions, 2), "conversion_value": round(m.conversions_value, 2)}


def run(a):
    cid = G.customer_id(a.customer_id)
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=a.days - 1)
    when = f"segments.date BETWEEN '{start}' AND '{end}'"
    g = G.client()
    rows = []
    if a.report == "campaign_daily":
        q = (f"SELECT segments.date, campaign.id, campaign.name, campaign.advertising_channel_type, "
             f"campaign_budget.amount_micros, {M}, metrics.search_impression_share, "
             f"metrics.search_budget_lost_impression_share, metrics.search_rank_lost_impression_share "
             f"FROM campaign WHERE {when} AND campaign.status != 'REMOVED'")
        for r in G.query(g, cid, q):
            ct = r.campaign.advertising_channel_type.name
            rows.append({"date": r.segments.date, "platform": "google", "campaign": r.campaign.name,
                         "campaign_id": r.campaign.id, "channel_type": ct, **base(r),
                         "impression_share": r.metrics.search_impression_share or "",
                         "lost_is_budget": r.metrics.search_budget_lost_impression_share or "",
                         "lost_is_rank": r.metrics.search_rank_lost_impression_share or "",
                         "budget": round(r.campaign_budget.amount_micros / 1e6, 2),
                         "segment": seg(r.campaign.name, ct)})
    elif a.report == "search_terms":
        d = "segments.date, " if a.daily else ""
        q = (f"SELECT {d}search_term_view.search_term, campaign.name, ad_group.name, {M} "
             f"FROM search_term_view WHERE {when}")
        for r in G.query(g, cid, q):
            row = {"term": r.search_term_view.search_term, "campaign": r.campaign.name,
                   "ad_group": r.ad_group.name, "segment": seg(r.campaign.name), **base(r)}
            if a.daily:
                row = {"date": r.segments.date, **row}
            rows.append(row)
    elif a.report == "pmax_search_terms":
        if not a.campaign_id:
            sys.exit("--campaign-id is required (one PMax campaign at a time)")
        q = (f"SELECT campaign_search_term_insight.category_label, metrics.impressions, metrics.clicks, "
             f"metrics.conversions, metrics.conversions_value FROM campaign_search_term_insight "
             f"WHERE {when} AND campaign_search_term_insight.campaign_id = '{a.campaign_id}'")
        for r in G.query(g, cid, q):
            rows.append({"term": r.campaign_search_term_insight.category_label or "(uncategorized)",
                         "impressions": r.metrics.impressions, "clicks": r.metrics.clicks,
                         "conversions": round(r.metrics.conversions, 2),
                         "conversion_value": round(r.metrics.conversions_value, 2)})
    elif a.report == "keywords":
        q = ("SELECT campaign.name, ad_group.name, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, "
             "ad_group_criterion.status, ad_group_criterion.quality_info.quality_score, "
             "ad_group_criterion.quality_info.search_predicted_ctr, ad_group_criterion.quality_info.creative_quality_score, "
             f"ad_group_criterion.quality_info.post_click_quality_score, {M} FROM keyword_view WHERE {when}")
        for r in G.query(g, cid, q):
            c = r.ad_group_criterion
            rows.append({"campaign": r.campaign.name, "ad_group": r.ad_group.name, "keyword": c.keyword.text,
                         "match_type": c.keyword.match_type.name, "status": c.status.name,
                         "quality_score": c.quality_info.quality_score or "",
                         "expected_ctr": c.quality_info.search_predicted_ctr.name,
                         "ad_relevance": c.quality_info.creative_quality_score.name,
                         "landing_page": c.quality_info.post_click_quality_score.name,
                         "segment": seg(r.campaign.name), **base(r)})
    elif a.report == "ad_groups":
        for r in G.query(g, cid, f"SELECT campaign.name, ad_group.name, {M} FROM ad_group WHERE {when}"):
            rows.append({"campaign": r.campaign.name, "ad_group": r.ad_group.name, "segment": seg(r.campaign.name), **base(r)})
    elif a.report in ("landing_pages", "expanded_landing_pages"):
        view, field = (("landing_page_view", "unexpanded_final_url") if a.report == "landing_pages"
                       else ("expanded_landing_page_view", "expanded_final_url"))
        for r in G.query(g, cid, f"SELECT campaign.name, {view}.{field}, {M} FROM {view} WHERE {when}"):
            rows.append({"campaign": r.campaign.name, "url": getattr(getattr(r, view), field),
                         "segment": seg(r.campaign.name), **base(r)})
    elif a.report == "by":
        dim = {"device": "segments.device", "hour": "segments.hour", "day_of_week": "segments.day_of_week",
               "network": "segments.ad_network_type"}[a.dimension]
        for r in G.query(g, cid, f"SELECT campaign.name, {dim}, {M} FROM campaign WHERE {when}"):
            v = getattr(r.segments, dim.split(".")[1])
            rows.append({"campaign": r.campaign.name, a.dimension: getattr(v, "name", v),
                         "segment": seg(r.campaign.name), **base(r)})
    elif a.report == "pmax_networks":
        q = (f"SELECT campaign.name, segments.ad_network_type, {M} FROM campaign WHERE {when} "
             "AND campaign.advertising_channel_type = 'PERFORMANCE_MAX'")
        for r in G.query(g, cid, q):
            rows.append({"campaign": r.campaign.name, "network": r.segments.ad_network_type.name, **base(r)})
    elif a.report == "change_history":
        start_ch = max(start, end - timedelta(days=29))  # the API keeps 30 days
        q = ("SELECT change_event.change_date_time, change_event.change_resource_type, "
             "change_event.resource_change_operation, change_event.client_type, change_event.user_email, "
             "change_event.changed_fields, change_event.campaign FROM change_event "
             f"WHERE change_event.change_date_time >= '{start_ch}' AND change_event.change_date_time <= '{end} 23:59:59' "
             "ORDER BY change_event.change_date_time DESC LIMIT 10000")
        for r in G.query(g, cid, q):
            e = r.change_event
            rows.append({"when": e.change_date_time, "resource": e.change_resource_type.name,
                         "operation": e.resource_change_operation.name, "made_by": e.user_email,
                         "via": e.client_type.name, "fields": ",".join(e.changed_fields.paths),
                         "campaign": e.campaign})
    elif a.report == "gaql":
        if not a.query:
            sys.exit("--query is required")
        for r in G.query(g, cid, a.query):
            rows.append({"row": str(r).replace("\n", " ")})
    write(rows, a.out)


def write(rows, out):
    if not rows:
        print("No rows.", file=sys.stderr)
        return
    f = open(out, "w", newline="") if out else sys.stdout
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
    if out:
        f.close()
        print(f"{len(rows)} rows -> {out}", file=sys.stderr)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report", choices=("campaign_daily", "search_terms", "pmax_search_terms", "keywords", "ad_groups",
                                       "landing_pages", "expanded_landing_pages", "by", "pmax_networks",
                                       "change_history", "gaql"))
    ap.add_argument("--customer-id"); ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--daily", action="store_true", help="search_terms: one row per day (for whole-week windows)")
    ap.add_argument("--dimension", default="device", choices=("device", "hour", "day_of_week", "network"))
    ap.add_argument("--campaign-id"); ap.add_argument("--query"); ap.add_argument("--out")
    run(ap.parse_args())
