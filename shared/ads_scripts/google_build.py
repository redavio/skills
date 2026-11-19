"""Build Search campaigns on Google Ads from a plan file. Campaigns are created PAUSED.

  python3 google_build.py plan.json --check     offline: limits and playbook rules, no API call
  python3 google_build.py plan.json             dry run: Google validates every operation, saves nothing
  python3 google_build.py plan.json --live      create (only after the person's explicit yes), then read back

Everything goes in ONE atomic request with temporary IDs: it all lands or nothing does.
Aborts if a campaign name already exists. Children (ad groups, keywords, ads) are ENABLED inside
PAUSED campaigns: switching a campaign on makes all of it live. The plan format is in
references/plan-format.md of the build skill.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for p in (HERE.parent, HERE.parent.parent / "shared"):
    if (p / "perfos").is_dir():
        sys.path.insert(0, str(p))


def check(plan: dict) -> tuple[list[str], list[str]]:
    from perfos import fencing, limits, naming
    errs, warns = [], []
    names = [c["name"] for c in plan.get("campaigns", [])]
    if len(set(names)) != len(names):
        errs.append("duplicate campaign names")
    a = plan.get("account_assets") or {}
    errs += limits.check_assets([(s["text"], s.get("description1", ""), s.get("description2", "")) for s in a.get("sitelinks", [])],
                                a.get("callouts", []), (a.get("snippet") or {}).get("header"), (a.get("snippet") or {}).get("values", []))
    for lst in plan.get("shared_negative_lists", []):
        errs += fencing.check_negatives([tuple(n) for n in lst["negatives"]], plan.get("protected_terms", []))
    for c in plan.get("campaigns", []):
        if not naming.segment(c["name"]):
            warns.append(f"{c['name']}: name doesn't follow channel|type|theme|geo|language; reports can't split brand from non-brand")
        if not c.get("daily_budget") or c["daily_budget"] <= 0:
            errs.append(f"{c['name']}: daily_budget missing")
        if c.get("bidding", "max_conversions") not in ("max_conversions", "max_conversion_value"):
            errs.append(f"{c['name']}: bidding must be max_conversions or max_conversion_value (smart bidding only)")
        if c.get("target_cpa") or c.get("target_roas"):
            warns.append(f"{c['name']}: has a target at launch. Playbook: no target on a new campaign; add it once there's data "
                         "(~30 conversions in 30 days for tCPA, 15+ with values for tROAS). OK for inherited history.")
        errs += [f"{c['name']}: {e}" for e in fencing.check_negatives([tuple(n) for n in c.get("negatives", [])], plan.get("protected_terms", []))]
        if not c.get("ad_groups"):
            errs.append(f"{c['name']}: no ad groups")
        for g in c.get("ad_groups", []):
            where = f"{c['name']} / {g['name']}"
            if not g.get("keywords"):
                errs.append(f"{where}: no keywords")
            if not (g.get("final_url") or plan.get("home_url")):
                errs.append(f"{where}: no final URL")
            errs += [f"{where}: {e}" for e in limits.check_rsa(g.get("headlines", []), g.get("descriptions", []),
                                                               g.get("path1", ""), g.get("path2", ""), want_full=False)]
            if len(g.get("headlines", [])) < 15 or len(g.get("descriptions", [])) < 4:
                warns.append(f"{where}: standard is 15 headlines and 4 descriptions")
            # ad-group negatives are fencing (other ad groups' own keywords, exact): only the no-broad rule applies
            errs += [f"{where}: {e}" for e in fencing.check_negatives([tuple(n) for n in g.get("negatives", [])])]
    return errs, warns


def build(plan: dict, cid: str, live: bool):
    import _google as G
    g = G.client(); E = g.enums
    existing = {r.campaign.name for r in G.query(g, cid, "SELECT campaign.name FROM campaign WHERE campaign.status != 'REMOVED'")}
    clash = [c["name"] for c in plan["campaigns"] if c["name"] in existing]
    if clash:
        sys.exit(f"ABORT: campaigns already exist: {clash}")
    portfolios_have = {r.bidding_strategy.name: r.bidding_strategy.resource_name
                       for r in G.query(g, cid, "SELECT bidding_strategy.name, bidding_strategy.resource_name FROM bidding_strategy")}
    ops, n = [], [0]

    def tmp(kind):
        n[0] -= 1
        return f"customers/{cid}/{kind}/{n[0]}"

    def mop(field):
        m = g.get_type("MutateOperation")
        ops.append(m)
        return getattr(m, field).create

    def mt(m):
        return getattr(E.KeywordMatchTypeEnum, m.upper())

    # shared negative lists
    lists = {}
    for lst in plan.get("shared_negative_lists", []):
        ss = mop("shared_set_operation"); ss.resource_name = rn = tmp("sharedSets")
        ss.name = lst["name"]; ss.type_ = E.SharedSetTypeEnum.NEGATIVE_KEYWORDS
        lists[lst["name"]] = rn
        for t, m in lst["negatives"]:
            sc = mop("shared_criterion_operation"); sc.shared_set = rn; sc.keyword.text = t; sc.keyword.match_type = mt(m)
    # account-level assets
    a = plan.get("account_assets") or {}
    for s in a.get("sitelinks", []):
        x = mop("asset_operation"); x.resource_name = rn = tmp("assets")
        x.final_urls.append(s["url"]); x.sitelink_asset.link_text = s["text"]
        if s.get("description1"):
            x.sitelink_asset.description1 = s["description1"]; x.sitelink_asset.description2 = s.get("description2", "")
        ca = mop("customer_asset_operation"); ca.asset = rn; ca.field_type = E.AssetFieldTypeEnum.SITELINK
    for t in a.get("callouts", []):
        x = mop("asset_operation"); x.resource_name = rn = tmp("assets"); x.callout_asset.callout_text = t
        ca = mop("customer_asset_operation"); ca.asset = rn; ca.field_type = E.AssetFieldTypeEnum.CALLOUT
    if a.get("snippet"):
        x = mop("asset_operation"); x.resource_name = rn = tmp("assets")
        x.structured_snippet_asset.header = a["snippet"]["header"]; x.structured_snippet_asset.values.extend(a["snippet"]["values"])
        ca = mop("customer_asset_operation"); ca.asset = rn; ca.field_type = E.AssetFieldTypeEnum.STRUCTURED_SNIPPET
    # portfolios (one per campaign type; reused if one with that name exists)
    ports = {}
    for c in plan["campaigns"]:
        p = c.get("portfolio")
        if p and p not in ports:
            if p in portfolios_have:
                ports[p] = portfolios_have[p]
                continue
            bs = mop("bidding_strategy_operation"); bs.resource_name = ports[p] = tmp("biddingStrategies"); bs.name = p
            if c.get("bidding") == "max_conversion_value":
                bs.maximize_conversion_value = g.get_type("MaximizeConversionValue")
                if c.get("target_roas"):
                    bs.maximize_conversion_value.target_roas = c["target_roas"]
            else:
                bs.maximize_conversions = g.get_type("MaximizeConversions")
                if c.get("target_cpa"):
                    bs.maximize_conversions.target_cpa_micros = int(c["target_cpa"] * 1e6)
    home = plan.get("home_url")
    for c in plan["campaigns"]:
        b = mop("campaign_budget_operation"); b.resource_name = brn = tmp("campaignBudgets")
        b.name = f"{c['name']} budget"; b.amount_micros = int(round(c["daily_budget"] * 1e6))
        b.delivery_method = E.BudgetDeliveryMethodEnum.STANDARD; b.explicitly_shared = False
        cp = mop("campaign_operation"); cp.resource_name = crn = tmp("campaigns")
        cp.name = c["name"]; cp.status = E.CampaignStatusEnum.PAUSED
        cp.advertising_channel_type = E.AdvertisingChannelTypeEnum.SEARCH; cp.campaign_budget = brn
        if c.get("portfolio"):
            cp.bidding_strategy = ports[c["portfolio"]]
        elif c.get("bidding") == "max_conversion_value":
            cp.maximize_conversion_value = g.get_type("MaximizeConversionValue")
            if c.get("target_roas"):
                cp.maximize_conversion_value.target_roas = c["target_roas"]
        else:
            cp.maximize_conversions = g.get_type("MaximizeConversions")
            if c.get("target_cpa"):
                cp.maximize_conversions.target_cpa_micros = int(c["target_cpa"] * 1e6)
        ns = cp.network_settings  # Search only: partners and Display off
        ns.target_google_search = True; ns.target_search_network = False
        ns.target_content_network = False; ns.target_partner_search_network = False
        cp.geo_target_type_setting.positive_geo_target_type = E.PositiveGeoTargetTypeEnum.PRESENCE
        if hasattr(E, "EuPoliticalAdvertisingStatusEnum"):
            cp.contains_eu_political_advertising = E.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
        if c.get("ai_max"):
            cp.ai_max_setting.enable_ai_max = True
        for loc in c.get("locations", plan.get("locations", [])):
            cc = mop("campaign_criterion_operation"); cc.campaign = crn; cc.location.geo_target_constant = f"geoTargetConstants/{loc}"
        for lang in c.get("languages", plan.get("languages", [])):
            cc = mop("campaign_criterion_operation"); cc.campaign = crn; cc.language.language_constant = f"languageConstants/{lang}"
        for t, m in c.get("negatives", []):
            cc = mop("campaign_criterion_operation"); cc.campaign = crn; cc.negative = True
            cc.keyword.text = t; cc.keyword.match_type = mt(m)
        for path in c.get("url_exclusions", []):
            cc = mop("campaign_criterion_operation"); cc.campaign = crn; cc.negative = True
            cc.webpage.criterion_name = f"Exclude {path}"
            cond = g.get_type("WebpageConditionInfo")
            cond.operand = E.WebpageConditionOperandEnum.URL; cond.operator = E.WebpageConditionOperatorEnum.CONTAINS
            cond.argument = path
            cc.webpage.conditions.append(cond)
        for name in c.get("shared_negative_lists", []):
            if name not in lists:
                sys.exit(f"{c['name']}: shared list '{name}' isn't in shared_negative_lists")
            cs = mop("campaign_shared_set_operation"); cs.campaign = crn; cs.shared_set = lists[name]
        for ag in c["ad_groups"]:
            x = mop("ad_group_operation"); x.resource_name = agrn = tmp("adGroups")
            x.name = ag["name"]; x.campaign = crn; x.status = E.AdGroupStatusEnum.ENABLED; x.type_ = E.AdGroupTypeEnum.SEARCH_STANDARD
            for t, m in ag["keywords"]:
                k = mop("ad_group_criterion_operation"); k.ad_group = agrn; k.status = E.AdGroupCriterionStatusEnum.ENABLED
                k.keyword.text = t; k.keyword.match_type = mt(m)
            for t, m in ag.get("negatives", []):
                k = mop("ad_group_criterion_operation"); k.ad_group = agrn; k.negative = True
                k.keyword.text = t; k.keyword.match_type = mt(m)
            ad = mop("ad_group_ad_operation"); ad.ad_group = agrn; ad.status = E.AdGroupAdStatusEnum.ENABLED
            ad.ad.final_urls.append(ag.get("final_url") or home)
            for h in ag["headlines"]:
                t = g.get_type("AdTextAsset"); t.text = h; ad.ad.responsive_search_ad.headlines.append(t)
            for d in ag["descriptions"]:
                t = g.get_type("AdTextAsset"); t.text = d; ad.ad.responsive_search_ad.descriptions.append(t)
            if ag.get("path1"):
                ad.ad.responsive_search_ad.path1 = ag["path1"]
            if ag.get("path2"):
                ad.ad.responsive_search_ad.path2 = ag["path2"]
    print(f"{len(ops)} operations, {'LIVE' if live else 'validate only'}")
    g.get_service("GoogleAdsService").mutate(customer_id=cid, mutate_operations=ops, validate_only=not live)
    if not live:
        print("Google accepted every operation. Nothing saved. Build with --live only after the person's yes.")
        return
    readback(G, g, cid, plan)


def readback(G, g, cid, plan):
    """Count what exists per campaign and compare with the plan. Trust this, not the create response."""
    bad = False
    for c in plan["campaigns"]:
        C = G.esc(c["name"])
        st = G.query(g, cid, f"SELECT campaign.status FROM campaign WHERE campaign.name = '{C}' AND campaign.status != 'REMOVED'")
        ags = G.query(g, cid, f"SELECT ad_group.id FROM ad_group WHERE campaign.name = '{C}' AND ad_group.status != 'REMOVED'")
        kws = G.query(g, cid, "SELECT ad_group_criterion.criterion_id FROM ad_group_criterion WHERE "
                      f"campaign.name = '{C}' AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE "
                      "AND ad_group_criterion.status != 'REMOVED'")
        ads = G.query(g, cid, f"SELECT ad_group_ad.ad.id FROM ad_group_ad WHERE campaign.name = '{C}' AND ad_group_ad.status != 'REMOVED'")
        want = (len(c["ad_groups"]), sum(len(a["keywords"]) for a in c["ad_groups"]), len(c["ad_groups"]))
        have = (len(ags), len(kws), len(ads))
        status = st[0].campaign.status.name if st else "MISSING"
        ok = have == want and status == "PAUSED"
        bad |= not ok
        print(f"{'OK ' if ok else 'BAD'} {c['name']}: status {status}, ad groups {have[0]}/{want[0]}, "
              f"keywords {have[1]}/{want[1]}, ads {have[2]}/{want[2]}")
    print("READ-BACK:", "matches the plan" if not bad else "DOES NOT match the plan: stop and report")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan"); ap.add_argument("--customer-id"); ap.add_argument("--check", action="store_true")
    ap.add_argument("--live", action="store_true")
    a = ap.parse_args()
    plan = json.loads(Path(a.plan).read_text())
    errs, warns = check(plan)
    for w in warns:
        print("WARN", w)
    if errs:
        print("PLAN CHECK FAILED"); print("\n".join(errs)); sys.exit(1)
    print("plan check OK")
    if a.check:
        sys.exit(0)
    import _google as G
    build(plan, G.customer_id(a.customer_id), a.live)
