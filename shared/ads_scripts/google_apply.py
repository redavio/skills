"""ONE approved change to a Google Ads account, then a read-back. Dry run by default.

  python3 google_apply.py negative --campaign C --text "free trial" [--match PHRASE]
  python3 google_apply.py keyword  --campaign C --ad-group G --text T --match EXACT
  python3 google_apply.py pause    --campaign C --ad-group G --text T --match EXACT
  python3 google_apply.py budget   --campaign C --daily 120
  python3 google_apply.py target   --campaign C --target-cpa 180 | --target-roas 4.5
  python3 google_apply.py campaign-status --campaign C --status ENABLED|PAUSED
Add --live to apply. Never run --live without the person's explicit yes for THIS change.
Dry run = Google validates the change without saving it. Success is confirmed by the
read-back, never by the API's "success" response. No broad negatives (refused).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _google as G  # noqa: E402

MATCH = ("EXACT", "PHRASE", "BROAD")
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("change", choices=("negative", "keyword", "pause", "budget", "target", "campaign-status"))
ap.add_argument("--customer-id"); ap.add_argument("--campaign", required=True); ap.add_argument("--ad-group")
ap.add_argument("--text"); ap.add_argument("--match", default="PHRASE", choices=MATCH)
ap.add_argument("--daily", type=float); ap.add_argument("--target-cpa", type=float); ap.add_argument("--target-roas", type=float)
ap.add_argument("--status", choices=("ENABLED", "PAUSED")); ap.add_argument("--live", action="store_true")
a = ap.parse_args()
if a.change in ("keyword", "pause") and not (a.ad_group and a.text):
    sys.exit("--ad-group and --text are required")
if a.change == "negative" and not a.text:
    sys.exit("--text is required")
if a.change == "negative" and a.match == "BROAD":
    sys.exit("No broad negatives. Use PHRASE (default), or EXACT to isolate a head term.")
if a.change == "budget" and not a.daily:
    sys.exit("--daily is required")
if a.change == "target" and not (a.target_cpa or a.target_roas):
    sys.exit("--target-cpa or --target-roas is required")
if a.change == "campaign-status" and not a.status:
    sys.exit("--status is required")

cid = G.customer_id(a.customer_id)
g = G.client(); E = g.enums
from google.api_core import protobuf_helpers  # noqa: E402

print(f"{'LIVE' if a.live else 'DRY RUN'}: {a.change} on '{a.campaign}'" + (f" / '{a.ad_group}'" if a.ad_group else ""))
C = G.esc(a.campaign)
camp = G.query(g, cid, "SELECT campaign.resource_name, campaign.campaign_budget, campaign.status, campaign.bidding_strategy_type, "
               "campaign.bidding_strategy, campaign_budget.explicitly_shared, campaign_budget.amount_micros "
               f"FROM campaign WHERE campaign.name = '{C}' AND campaign.status != 'REMOVED'")
if len(camp) != 1:
    sys.exit(f"Expected 1 campaign named '{a.campaign}', found {len(camp)}")
camp = camp[0]


def mutate(service, method, req_type, op):
    req = g.get_type(req_type)
    req.customer_id = cid
    req.operations.append(op)
    req.validate_only = not a.live
    getattr(g.get_service(service), method)(request=req)


def done(ok, detail=""):
    print("READ-BACK:", "confirmed" if ok else "NOT CONFIRMED", detail)
    sys.exit(0 if ok else 1)


neg_q = ("SELECT campaign_criterion.keyword.text FROM campaign_criterion WHERE campaign.name = '{c}' "
         "AND campaign_criterion.negative = TRUE AND campaign_criterion.keyword.text = '{t}' "
         "AND campaign_criterion.keyword.match_type = '{m}'")
kw_q = ("SELECT ad_group_criterion.resource_name, ad_group_criterion.status FROM ad_group_criterion "
        "WHERE campaign.name = '{c}' AND ad_group.name = '{g}' AND ad_group_criterion.type = 'KEYWORD' "
        "AND ad_group_criterion.negative = FALSE AND ad_group_criterion.keyword.text = '{t}' "
        "AND ad_group_criterion.keyword.match_type = '{m}' AND ad_group_criterion.status != 'REMOVED'")

if a.change == "negative":
    q = neg_q.format(c=C, t=G.esc(a.text), m=a.match)
    if G.query(g, cid, q):
        sys.exit("Already there. Nothing to do.")
    op = g.get_type("CampaignCriterionOperation"); cc = op.create
    cc.campaign = camp.campaign.resource_name; cc.negative = True
    cc.keyword.text = a.text; cc.keyword.match_type = getattr(E.KeywordMatchTypeEnum, a.match)
    mutate("CampaignCriterionService", "mutate_campaign_criteria", "MutateCampaignCriteriaRequest", op)
    if a.live:
        done(len(G.query(g, cid, q)) == 1)

elif a.change in ("keyword", "pause"):
    ag = G.query(g, cid, f"SELECT ad_group.resource_name FROM ad_group WHERE campaign.name = '{C}' "
                 f"AND ad_group.name = '{G.esc(a.ad_group)}' AND ad_group.status != 'REMOVED'")
    if len(ag) != 1:
        sys.exit(f"Expected 1 ad group named '{a.ad_group}', found {len(ag)}")
    q = kw_q.format(c=C, g=G.esc(a.ad_group), t=G.esc(a.text), m=a.match)
    found = G.query(g, cid, q)
    op = g.get_type("AdGroupCriterionOperation")
    if a.change == "keyword":
        if found:
            sys.exit("Already there. Nothing to do.")
        c = op.create; c.ad_group = ag[0].ad_group.resource_name; c.status = E.AdGroupCriterionStatusEnum.ENABLED
        c.keyword.text = a.text; c.keyword.match_type = getattr(E.KeywordMatchTypeEnum, a.match)
    else:
        if len(found) != 1:
            sys.exit(f"Expected 1 matching keyword, found {len(found)}")
        u = op.update; u.resource_name = found[0].ad_group_criterion.resource_name
        u.status = E.AdGroupCriterionStatusEnum.PAUSED
        g.copy_from(op.update_mask, protobuf_helpers.field_mask(None, u._pb))
    mutate("AdGroupCriterionService", "mutate_ad_group_criteria", "MutateAdGroupCriteriaRequest", op)
    if a.live:
        rows = G.query(g, cid, q)
        want = "PAUSED" if a.change == "pause" else "ENABLED"
        done(len(rows) == 1 and rows[0].ad_group_criterion.status.name == want)

elif a.change == "budget":
    if camp.campaign_budget.explicitly_shared:
        sys.exit("This campaign uses a shared budget: changing it moves every campaign on it. Stop and ask.")
    before = camp.campaign_budget.amount_micros / 1e6
    print(f"budget ${before:,.2f} -> ${a.daily:,.2f}/day ({(a.daily / before - 1):+.0%})" if before else "")
    op = g.get_type("CampaignBudgetOperation"); u = op.update
    u.resource_name = camp.campaign.campaign_budget; u.amount_micros = int(round(a.daily * 1e6))
    op.update_mask.paths.append("amount_micros")
    mutate("CampaignBudgetService", "mutate_campaign_budgets", "MutateCampaignBudgetsRequest", op)
    if a.live:
        r = G.query(g, cid, f"SELECT campaign_budget.amount_micros FROM campaign WHERE campaign.name = '{C}' AND campaign.status != 'REMOVED'")
        done(abs(r[0].campaign_budget.amount_micros / 1e6 - a.daily) < 0.01, f"(${r[0].campaign_budget.amount_micros / 1e6:,.2f}/day)")

elif a.change == "target":
    if camp.campaign.bidding_strategy:
        sys.exit("This campaign is in a portfolio: the target lives on the portfolio and moves every campaign in it. "
                 "Change it there, with the person's yes.")
    bst = camp.campaign.bidding_strategy_type.name
    op = g.get_type("CampaignOperation"); u = op.update; u.resource_name = camp.campaign.resource_name
    if a.target_cpa:
        if bst != "MAXIMIZE_CONVERSIONS":
            sys.exit(f"Target CPA sits on Maximize Conversions; this campaign is {bst}.")
        u.maximize_conversions.target_cpa_micros = int(round(a.target_cpa * 1e6))
        op.update_mask.paths.append("maximize_conversions.target_cpa_micros")
    else:
        if bst != "MAXIMIZE_CONVERSION_VALUE":
            sys.exit(f"Target ROAS sits on Maximize Conversion Value; this campaign is {bst}.")
        u.maximize_conversion_value.target_roas = a.target_roas
        op.update_mask.paths.append("maximize_conversion_value.target_roas")
    mutate("CampaignService", "mutate_campaigns", "MutateCampaignsRequest", op)
    if a.live:
        r = G.query(g, cid, "SELECT campaign.maximize_conversions.target_cpa_micros, campaign.maximize_conversion_value.target_roas "
                    f"FROM campaign WHERE campaign.name = '{C}' AND campaign.status != 'REMOVED'")[0].campaign
        ok = (abs(r.maximize_conversions.target_cpa_micros / 1e6 - a.target_cpa) < 0.01) if a.target_cpa else \
             (abs(r.maximize_conversion_value.target_roas - a.target_roas) < 1e-6)
        done(ok)

elif a.change == "campaign-status":
    op = g.get_type("CampaignOperation"); u = op.update; u.resource_name = camp.campaign.resource_name
    u.status = getattr(E.CampaignStatusEnum, a.status); op.update_mask.paths.append("status")
    mutate("CampaignService", "mutate_campaigns", "MutateCampaignsRequest", op)
    if a.live:
        r = G.query(g, cid, f"SELECT campaign.status FROM campaign WHERE campaign.name = '{C}' AND campaign.status != 'REMOVED'")
        done(r[0].campaign.status.name == a.status)

print("Validated by Google. Nothing saved. Add --live to apply, only with the person's yes.")
