"""Standard data shapes. Every connector produces these; every tool consumes them.

Channel is a field, so paid social, SEO or any other channel plugs in without new shapes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

# Segments are separate line items everywhere (foundations/strategy-planning.md).
SEGMENTS = ("brand", "nonbrand", "competitor", "pmax")
LEVELS = ("campaign", "ad_group", "keyword", "search_term", "search_theme",
          "audience", "geo", "device", "hour", "network", "placement", "ad", "landing_page")


@dataclass
class FactRow:
    """One day of ad platform stats for one entity. Platforms are the source of truth here."""
    date: date
    channel: str                  # "paid_search", later "paid_social", ...
    platform: str                 # "google", "bing", ...
    account_id: str
    campaign_id: str
    campaign_name: str
    segment: str                  # brand | nonbrand | competitor | pmax
    level: str = "campaign"
    entity_id: str = ""
    entity_name: str = ""
    impressions: float = 0.0
    clicks: float = 0.0
    cost: float = 0.0
    conversions: float = 0.0      # in-platform primary conversion (e.g. high-fit lead)
    conversion_value: float = 0.0
    eligible_impressions: float | None = None   # impressions / impression share, for IS rollups
    budget: float | None = None
    lost_is_budget: float | None = None


@dataclass
class Touch:
    ts: datetime
    source: str
    medium: str = ""
    campaign: str = ""


@dataclass
class CrmRecord:
    """One lead and its journey. The CRM is the source of truth for funnel stages."""
    lead_id: str
    created: date
    click_id: str | None = None          # GCLID / MSCLKID
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None      # campaign name slug (NAMING.md: name with | -> -)
    utm_content: str | None = None       # ad group ID
    utm_term: str | None = None          # keyword
    campaignid: str | None = None        # campaign ID from the suffix's campaignid parameter
    mql_date: date | None = None
    sql_date: date | None = None         # meeting booked
    s2_date: date | None = None          # qualified opportunity
    won_date: date | None = None
    pipeline_value: float = 0.0
    won_value: float = 0.0
    touches: list[Touch] = field(default_factory=list)
    # set by matching (connectors/matching.py)
    platform: str | None = None
    campaign_id: str | None = None
    match_method: str | None = None      # click_id | utm | unmatched


@dataclass
class Goal:
    segment: str            # a segment, "total", or a platform
    metric: str
    value: float
    period_start: date
    period_end: date


@dataclass
class Change:
    """Change log entry (foundations/change-log.md)."""
    ts: datetime
    platform: str
    account_id: str
    entity_id: str
    field: str
    old: str
    new: str
    made_by: str            # "operator", "client", "platform"
    category: str
    safety: str             # routine | material | destructive
    why: str = ""
