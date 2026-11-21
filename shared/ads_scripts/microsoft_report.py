"""Pull a Microsoft Advertising report to CSV in the shape the perfos commands read. Read only.

  python3 microsoft_report.py campaign_daily --days 28 --out campaigns_ms.csv
  python3 microsoft_report.py search_terms --days 28 [--daily] --out terms_ms.csv
  python3 microsoft_report.py audience_campaigns | audience_placements | professional_demographics --days 28
Uses the Reporting service (submit, poll, download). Data runs through yesterday.
"""
from __future__ import annotations

import argparse
import csv
import io
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _microsoft as MS  # noqa: E402

for p in (HERE.parent,):
    if (p / "perfos").is_dir():
        sys.path.insert(0, str(p))
try:
    from perfos import naming
except ImportError:
    naming = None

COLUMNS = {
    "campaign_daily": ("CampaignPerformanceReportRequest", "AccountThroughCampaignReportScope",
                       ["TimePeriod", "CampaignId", "CampaignName", "Impressions", "Clicks", "Spend", "Conversions",
                        "Revenue", "ImpressionSharePercent", "ImpressionLostToBudgetPercent", "ImpressionLostToRankAggPercent"]),
    "search_terms": ("SearchQueryPerformanceReportRequest", "AccountThroughAdGroupReportScope",
                     ["SearchQuery", "CampaignName", "AdGroupName", "Impressions", "Clicks", "Spend", "Conversions", "Revenue"]),
    # Audience ads (Microsoft Audience Network): campaign totals, where ads showed, and who saw them (LinkedIn profile).
    "audience_campaigns": ("CampaignPerformanceReportRequest", "AccountThroughCampaignReportScope",
                           ["CampaignId", "CampaignName", "CampaignType", "Impressions", "Clicks", "Spend", "Conversions", "Revenue"]),
    "audience_placements": ("PublisherUsagePerformanceReportRequest", "AccountThroughAdGroupReportScope",
                            ["PublisherUrl", "CampaignName", "AdGroupName", "Impressions", "Clicks", "Spend", "Conversions", "Revenue"]),
    "professional_demographics": ("ProfessionalDemographicsAudienceReportRequest", "AccountThroughAdGroupReportScope",
                                  ["CompanyName", "IndustryName", "JobFunctionName", "CampaignName", "AdGroupName",
                                   "Impressions", "Clicks", "Spend", "Conversions", "Revenue"]),
}


def _num(v):
    v = (v or "").replace(",", "").replace("%", "").strip()
    return float(v) if v not in ("", "--") else 0.0


def run(a):
    from bingads.v13.reporting import ReportingDownloadParameters, ReportingServiceManager
    acct = MS.account_id(a.account_id)
    ad = MS.auth(acct)
    rs = MS.service("ReportingService", ad)
    F = rs.factory
    req_type, scope_type, cols = COLUMNS[a.report]
    if a.report == "search_terms" and a.daily:
        cols = ["TimePeriod"] + cols
    req = F.create(req_type)
    req.Aggregation = "Daily" if (a.report == "campaign_daily" or a.daily) else "Summary"
    req.ExcludeColumnHeaders = False; req.ExcludeReportFooter = True; req.ExcludeReportHeader = True
    req.Format = "Csv"; req.ReturnOnlyCompleteData = False; req.ReportName = a.report
    scope = F.create(scope_type); scope.AccountIds = {"long": [acct]}
    for k in ("Campaigns", "AdGroups"):
        if hasattr(scope, k):
            setattr(scope, k, None)
    req.Scope = scope
    end = date.today() - timedelta(days=1); start = end - timedelta(days=a.days - 1)
    t = F.create("ReportTime")
    for attr, d in (("CustomDateRangeStart", start), ("CustomDateRangeEnd", end)):
        x = F.create("Date"); x.Day, x.Month, x.Year = d.day, d.month, d.year
        setattr(t, attr, x)
    t.PredefinedTime = None; t.ReportTimeZone = "PacificTimeUSCanadaTijuana"
    req.Time = t
    col_type = req_type.replace("Request", "Column")
    arr = F.create(f"ArrayOf{col_type}")
    getattr(arr, col_type).extend(cols)
    req.Columns = arr
    with tempfile.TemporaryDirectory() as tmp:
        path = ReportingServiceManager(authorization_data=ad, poll_interval_in_milliseconds=5000,
                                       environment="production").download_file(
            ReportingDownloadParameters(report_request=req, result_file_directory=tmp, result_file_name="r.csv",
                                        overwrite_result_file=True, timeout_in_milliseconds=3600000))
        text = Path(path).read_text(encoding="utf-8-sig") if path else ""
    rows = []
    for r in csv.DictReader(io.StringIO(text)):
        base = {"impressions": _num(r.get("Impressions")), "clicks": _num(r.get("Clicks")), "cost": _num(r.get("Spend")),
                "conversions": _num(r.get("Conversions")), "conversion_value": _num(r.get("Revenue"))}
        camp = r.get("CampaignName", "")
        segment = (naming.segment(camp) or "unknown") if naming else ""
        if a.report == "campaign_daily":
            share = _num(r.get("ImpressionSharePercent")) / 100
            rows.append({"date": r["TimePeriod"], "platform": "microsoft", "campaign": camp, "campaign_id": r["CampaignId"],
                         **base, "impression_share": share or "",
                         "lost_is_budget": _num(r.get("ImpressionLostToBudgetPercent")) / 100 or "",
                         "lost_is_rank": _num(r.get("ImpressionLostToRankAggPercent")) / 100 or "", "segment": segment})
        elif a.report == "audience_campaigns":
            if "audience" not in (r.get("CampaignType") or "").lower():
                continue
            rows.append({"campaign": camp, "campaign_id": r["CampaignId"], "channel_type": r.get("CampaignType"), **base})
        elif a.report == "audience_placements":
            rows.append({"placement": r.get("PublisherUrl", ""), "network": "Microsoft Audience Network",
                         "campaign": camp, "ad_group": r.get("AdGroupName", ""), **base})
        elif a.report == "professional_demographics":
            rows.append({"company": r.get("CompanyName", ""), "industry": r.get("IndustryName", ""),
                         "job_function": r.get("JobFunctionName", ""), "campaign": camp, **base})
        else:
            row = {"term": r["SearchQuery"], "campaign": camp, "ad_group": r.get("AdGroupName", ""), "segment": segment, **base}
            if a.daily:
                row = {"date": r["TimePeriod"], **row}
            rows.append(row)
    if not rows:
        print("No rows.", file=sys.stderr); return
    f = open(a.out, "w", newline="") if a.out else sys.stdout
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} rows", file=sys.stderr)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report", choices=tuple(COLUMNS)); ap.add_argument("--account-id")
    ap.add_argument("--days", type=int, default=28); ap.add_argument("--daily", action="store_true"); ap.add_argument("--out")
    run(ap.parse_args())
