"""ONE approved change to a Microsoft Advertising account, then a read-back. Dry run by default.

  python3 microsoft_apply.py negative --campaign C --text "free trial" [--match PHRASE]
  python3 microsoft_apply.py keyword  --campaign C --ad-group G --text T --match EXACT
  python3 microsoft_apply.py pause    --campaign C --ad-group G --text T --match EXACT
  python3 microsoft_apply.py budget   --campaign C --daily 120
  python3 microsoft_apply.py campaign-status --campaign C --status Active|Paused
Microsoft has no validate-only: the dry run finds the target and stops. Add --live to apply, only
with the person's explicit yes for THIS change. Confirmed by read-back. No broad negatives.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _microsoft as MS  # noqa: E402

MT = {"EXACT": "Exact", "PHRASE": "Phrase", "BROAD": "Broad"}
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("change", choices=("negative", "keyword", "pause", "budget", "campaign-status"))
ap.add_argument("--account-id"); ap.add_argument("--campaign", required=True); ap.add_argument("--ad-group")
ap.add_argument("--text"); ap.add_argument("--match", default="PHRASE", choices=tuple(MT))
ap.add_argument("--daily", type=float); ap.add_argument("--status", choices=("Active", "Paused"))
ap.add_argument("--live", action="store_true")
a = ap.parse_args()
if a.change == "negative" and a.match == "BROAD":
    sys.exit("No broad negatives. Use PHRASE (default), or EXACT to isolate a head term.")
if a.change in ("keyword", "pause") and not (a.ad_group and a.text):
    sys.exit("--ad-group and --text are required")

acct = MS.account_id(a.account_id)
cm = MS.service("CampaignManagementService", MS.auth(acct))
new, arr = MS.factory_tools(cm)
print(f"{'LIVE' if a.live else 'DRY RUN'}: {a.change} on '{a.campaign}'" + (f" / '{a.ad_group}'" if a.ad_group else ""))
camps = [c for c in MS.items(cm.GetCampaignsByAccountId(AccountId=acct, CampaignType="Search"), "Campaign") if c.Name == a.campaign]
if len(camps) != 1:
    sys.exit(f"Expected 1 campaign named '{a.campaign}', found {len(camps)}")
camp = camps[0]


def stop_if_dry():
    if not a.live:
        print("Target found. Nothing saved (Microsoft has no validate-only). Add --live with the person's yes.")
        sys.exit(0)


def done(ok, detail=""):
    print("READ-BACK:", "confirmed" if ok else "NOT CONFIRMED", detail)
    sys.exit(0 if ok else 1)


def reread_campaign():
    return next(c for c in MS.items(cm.GetCampaignsByAccountId(AccountId=acct, CampaignType="Search"), "Campaign") if c.Id == camp.Id)


if a.change == "negative":
    def negs():
        r = cm.GetNegativeKeywordsByEntityIds(EntityIds={"long": [camp.Id]}, EntityType="Campaign", ParentEntityId=acct)
        return [n for e in MS.items(r, "EntityNegativeKeywords", "EntityNegativeKeyword")
                for n in MS.items(e, "NegativeKeywords", "NegativeKeyword") if n.Text == a.text and n.MatchType == MT[a.match]]
    if negs():
        sys.exit("Already there. Nothing to do.")
    stop_if_dry()
    MS.check("negative", cm.AddNegativeKeywordsToEntities(EntityNegativeKeywords=arr("EntityNegativeKeyword", [
        new("EntityNegativeKeyword", EntityId=camp.Id, EntityType="Campaign",
            NegativeKeywords=arr("NegativeKeyword", [new("NegativeKeyword", Text=a.text, MatchType=MT[a.match], Type="NegativeKeyword")]))])))
    done(len(negs()) == 1)

elif a.change in ("keyword", "pause"):
    ags = [g for g in MS.items(cm.GetAdGroupsByCampaignId(CampaignId=camp.Id), "AdGroup") if g.Name == a.ad_group]
    if len(ags) != 1:
        sys.exit(f"Expected 1 ad group named '{a.ad_group}', found {len(ags)}")
    agid = ags[0].Id

    def kws():
        return [k for k in MS.items(cm.GetKeywordsByAdGroupId(AdGroupId=agid), "Keyword")
                if k.Text == a.text and k.MatchType == MT[a.match] and k.Status != "Deleted"]
    found = kws()
    if a.change == "keyword":
        if found:
            sys.exit("Already there. Nothing to do.")
        stop_if_dry()
        MS.check("keyword", cm.AddKeywords(AdGroupId=agid, Keywords=arr("Keyword", [
            new("Keyword", Text=a.text, MatchType=MT[a.match], Status="Active")])))
        want = "Active"
    else:
        if len(found) != 1:
            sys.exit(f"Expected 1 matching keyword, found {len(found)}")
        stop_if_dry()
        MS.check("pause", cm.UpdateKeywords(AdGroupId=agid, Keywords=arr("Keyword", [new("Keyword", Id=found[0].Id, Status="Paused")])))
        want = "Paused"
    after = kws()
    done(len(after) == 1 and after[0].Status == want)

elif a.change == "budget":
    if not a.daily:
        sys.exit("--daily is required")
    if getattr(camp, "BudgetId", None):
        sys.exit("This campaign uses a shared budget: changing it moves every campaign on it. Stop and ask.")
    print(f"budget ${camp.DailyBudget:,.2f} -> ${a.daily:,.2f}/day")
    stop_if_dry()
    MS.check("budget", cm.UpdateCampaigns(AccountId=acct, Campaigns=arr("Campaign", [
        new("Campaign", Id=camp.Id, DailyBudget=a.daily)])))
    c = reread_campaign()
    done(abs(float(c.DailyBudget) - a.daily) < 0.01, f"(${float(c.DailyBudget):,.2f}/day)")

elif a.change == "campaign-status":
    if not a.status:
        sys.exit("--status is required")
    stop_if_dry()
    MS.check("status", cm.UpdateCampaigns(AccountId=acct, Campaigns=arr("Campaign", [new("Campaign", Id=camp.Id, Status=a.status)])))
    done(reread_campaign().Status == a.status)
