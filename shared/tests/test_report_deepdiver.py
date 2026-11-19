from datetime import date, timedelta

from perfos import metrics, parity, prune_promote, report
from perfos import matching
from perfos.diagnosis import deepdiver
from perfos.schema import CrmRecord, FactRow

START, END = date(2026, 10, 5), date(2026, 11, 1)


def facts():
    rows = []
    for i in range(56):
        d = date(2026, 9, 7) + timedelta(days=i)
        recent = d >= START
        rows.append(FactRow(d, "paid_search", "google", "a", "nb1", "search|nonbrand|w|us|en", "nonbrand",
                            impressions=1000, clicks=40, cost=280, conversions=2 if recent else 3,
                            eligible_impressions=2500))
        rows.append(FactRow(d, "paid_search", "bing", "b", "br1", "search|brand|b|us|en", "brand",
                            impressions=300, clicks=60, cost=120, conversions=6, eligible_impressions=330))
    return rows


def crm():
    out = []
    for i in range(56):
        d = date(2026, 9, 7) + timedelta(days=i)
        out.append(CrmRecord(f"L{i}", d, click_id=f"g{i}", mql_date=d, sql_date=d, s2_date=d,
                             pipeline_value=10000))
    return matching.match(out, {f"g{i}": ("google", "nb1") for i in range(56)})


def test_report_rows_and_driver_sentence():
    r = report.build(facts(), crm(), START, END, driver_kpi="cpa")
    keys = [row["key"] for row in r["rows"]]
    assert keys[:2] == ["brand", "nonbrand"] and "total" in keys and "google" in keys and "bing" in keys
    nb = next(row for row in r["rows"] if row["key"] == "nonbrand")
    assert "click to conversion rate drove 100%" in nb["driver"]
    assert nb["cells"]["s2s"]["value"] == 28


def test_impression_share_only_counts_search_rows():
    t = metrics.totals(facts(), [], START, END)["total"]
    assert 0 < t["impression_share"] < 1


def test_low_volume_factor_not_named():
    a = {"cpc": 2.0, "cvr": 0.03, "clicks": 10}
    b = {"cpc": 2.0, "cvr": 0.05}
    d = deepdiver.diagnose("cpa", a, b, min_volume={"clicks": 60})
    assert "No single lever" in d["sentence"]


def test_match_rate_and_utm_fallback():
    recs = [CrmRecord("1", START, click_id="x"), CrmRecord("2", START, utm_source="google", utm_campaign="nb1"),
            CrmRecord("3", START)]
    matching.match(recs, {"x": ("google", "nb1")})
    assert [r.match_method for r in recs] == ["click_id", "utm", "unmatched"]
    assert matching.match_rate(recs)["rate"] == 2 / 3


def test_prune_promote_proposes_negative():
    rows = [FactRow(START + timedelta(days=i), "paid_search", "google", "a", "nb1", "n", "nonbrand",
                    level="search_term", entity_id="free crm", entity_name="free crm", clicks=10, cost=30)
            for i in range(14)]
    p = prune_promote.run(rows, {"nonbrand": {"cvr": 0.05, "cpa": 150}})
    assert p[0]["verdict"] == "cut" and p[0]["proposal"] == "add as negative (exact)"


def test_parity_flags_drift():
    g = [{"type": "keyword", "campaign": "c", "ad_group": "a", "name": "crm", "match_type": "exact"}]
    b = [{"type": "keyword", "campaign": "c", "ad_group": "a", "name": "crm", "match_type": "phrase"}]
    assert parity.check(g, b)[0]["field"] == "match_type"
