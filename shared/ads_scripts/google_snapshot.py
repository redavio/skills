"""Read-only snapshot of a Google Ads account as JSON: settings, campaigns, conversions, shared
lists, assets, ads. The input to audit, launch-check, status and handoff. Nothing is changed.

  python3 google_snapshot.py [--customer-id 1234567890] [--out snapshot.json]
Any section the API version or account can't return is reported as unavailable, not guessed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _google as G  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--customer-id"); ap.add_argument("--out")
a = ap.parse_args()
cid = G.customer_id(a.customer_id)
g = G.client()
snap = {"customer_id": cid}


def section(name, gaql, fn):
    try:
        snap[name] = [fn(r) for r in G.query(g, cid, gaql)]
    except Exception as e:  # noqa: BLE001 - report, never guess
        snap[name] = {"unavailable": str(e).splitlines()[0][:200]}


section("account", "SELECT customer.descriptive_name, customer.currency_code, customer.time_zone, "
        "customer.auto_tagging_enabled, customer.final_url_suffix, "
        "customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled, "
        "customer.conversion_tracking_setting.accepted_customer_data_terms FROM customer",
        lambda r: {"name": r.customer.descriptive_name, "currency": r.customer.currency_code,
                   "time_zone": r.customer.time_zone, "auto_tagging": r.customer.auto_tagging_enabled,
                   "final_url_suffix": r.customer.final_url_suffix,
                   "enhanced_conversions_for_leads": r.customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled,
                   "customer_data_terms": r.customer.conversion_tracking_setting.accepted_customer_data_terms})
section("campaigns", "SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type, "
        "campaign.bidding_strategy_type, campaign.bidding_strategy, campaign.maximize_conversions.target_cpa_micros, "
        "campaign.maximize_conversion_value.target_roas, campaign_budget.amount_micros, "
        "campaign_budget.explicitly_shared, campaign.network_settings.target_search_network, "
        "campaign.network_settings.target_content_network, campaign.network_settings.target_partner_search_network, "
        "campaign.geo_target_type_setting.positive_geo_target_type, campaign.final_url_suffix "
        "FROM campaign WHERE campaign.status != 'REMOVED'",
        lambda r: {"id": r.campaign.id, "name": r.campaign.name, "status": r.campaign.status.name,
                   "type": r.campaign.advertising_channel_type.name,
                   "bidding": r.campaign.bidding_strategy_type.name, "portfolio": r.campaign.bidding_strategy,
                   "target_cpa": r.campaign.maximize_conversions.target_cpa_micros / 1e6 or None,
                   "target_roas": r.campaign.maximize_conversion_value.target_roas or None,
                   "daily_budget": r.campaign_budget.amount_micros / 1e6,
                   "shared_budget": r.campaign_budget.explicitly_shared,
                   "search_partners": r.campaign.network_settings.target_search_network,
                   "display": r.campaign.network_settings.target_content_network,
                   "location_option": r.campaign.geo_target_type_setting.positive_geo_target_type.name})
section("ai_max", "SELECT campaign.name, campaign.ai_max_setting.enable_ai_max FROM campaign "
        "WHERE campaign.advertising_channel_type = 'SEARCH' AND campaign.status != 'REMOVED'",
        lambda r: {"campaign": r.campaign.name, "ai_max": r.campaign.ai_max_setting.enable_ai_max})
section("conversion_actions", "SELECT conversion_action.name, conversion_action.status, conversion_action.type, "
        "conversion_action.category, conversion_action.primary_for_goal, conversion_action.counting_type, "
        "conversion_action.value_settings.default_value, conversion_action.click_through_lookback_window_days "
        "FROM conversion_action WHERE conversion_action.status != 'REMOVED'",
        lambda r: {"name": r.conversion_action.name, "status": r.conversion_action.status.name,
                   "type": r.conversion_action.type_.name, "category": r.conversion_action.category.name,
                   "primary": r.conversion_action.primary_for_goal,
                   "counting": r.conversion_action.counting_type.name,
                   "default_value": r.conversion_action.value_settings.default_value,
                   "lookback_days": r.conversion_action.click_through_lookback_window_days})
section("conversions_30d", "SELECT segments.conversion_action_name, metrics.all_conversions FROM customer "
        "WHERE segments.date DURING LAST_30_DAYS",
        lambda r: {"action": r.segments.conversion_action_name, "conversions": r.metrics.all_conversions})
section("shared_lists", "SELECT shared_set.name, shared_set.type, shared_set.member_count FROM shared_set "
        "WHERE shared_set.status = 'ENABLED'",
        lambda r: {"name": r.shared_set.name, "type": r.shared_set.type_.name, "members": r.shared_set.member_count})
section("account_assets", "SELECT customer_asset.field_type, customer_asset.status FROM customer_asset "
        "WHERE customer_asset.status = 'ENABLED'",
        lambda r: {"field_type": r.customer_asset.field_type.name})
section("ads", "SELECT campaign.name, ad_group.name, ad_group_ad.status, ad_group_ad.ad_strength, "
        "ad_group_ad.policy_summary.approval_status, ad_group_ad.ad.responsive_search_ad.headlines, "
        "ad_group_ad.ad.responsive_search_ad.descriptions FROM ad_group_ad "
        "WHERE ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD' AND ad_group_ad.status != 'REMOVED'",
        lambda r: {"campaign": r.campaign.name, "ad_group": r.ad_group.name, "status": r.ad_group_ad.status.name,
                   "strength": r.ad_group_ad.ad_strength.name,
                   "approval": r.ad_group_ad.policy_summary.approval_status.name,
                   "headlines": len(r.ad_group_ad.ad.responsive_search_ad.headlines),
                   "pinned": sum(1 for h in r.ad_group_ad.ad.responsive_search_ad.headlines if h.pinned_field.name not in ("UNSPECIFIED", "UNKNOWN")),
                   "descriptions": len(r.ad_group_ad.ad.responsive_search_ad.descriptions)})
section("ad_groups", "SELECT campaign.name, ad_group.name, ad_group.status FROM ad_group WHERE ad_group.status != 'REMOVED'",
        lambda r: {"campaign": r.campaign.name, "ad_group": r.ad_group.name, "status": r.ad_group.status.name})
text = json.dumps(snap, indent=2, default=str)
if a.out:
    Path(a.out).write_text(text)
    print(f"snapshot -> {a.out}", file=sys.stderr)
else:
    print(text)
