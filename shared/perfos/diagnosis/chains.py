"""Metric chains: which levers multiply into which KPI.

Split on levers, never outcomes (actions/diagnosis.md). Each factor must be a derived
metric in perfos.metrics.derive. Funnel stages are config: clients without SQLs drop that
stage by passing a custom chain, no code change.
"""
from __future__ import annotations

FUNNEL = ["impressions", "ctr", "cvr", "conv_to_mql", "mql_to_sql", "sql_to_s2", "s2_to_won"]

CHAINS: dict[str, dict] = {
    # volume KPIs
    "conversions": {"factors": [("impressions", 1), ("ctr", 1), ("cvr", 1)], "higher_is_better": True},
    "s2s": {"factors": [(f, 1) for f in FUNNEL[:-1]], "higher_is_better": True},
    "won": {"factors": [(f, 1) for f in FUNNEL], "higher_is_better": True},
    "pipeline": {"factors": [(f, 1) for f in FUNNEL[:-1]] + [("pipeline_per_s2", 1)], "higher_is_better": True},
    "won_value": {"factors": [(f, 1) for f in FUNNEL] + [("deal_value", 1)], "higher_is_better": True},
    # cost-per KPIs: CPC over the rates
    "cpa": {"factors": [("cpc", 1), ("cvr", -1)], "higher_is_better": False},
    "cost_per_s2": {"factors": [("cpc", 1), ("cvr", -1), ("conv_to_mql", -1), ("mql_to_sql", -1),
                                ("sql_to_s2", -1)], "higher_is_better": False},
    "cost_per_won": {"factors": [("cpc", 1), ("cvr", -1), ("conv_to_mql", -1), ("mql_to_sql", -1),
                                 ("sql_to_s2", -1), ("s2_to_won", -1)], "higher_is_better": False},
    # return KPIs
    "roas": {"factors": [("value_per_conversion", 1), ("cvr", 1), ("cpc", -1)], "higher_is_better": True},
    "pipeline_roas": {"factors": [("pipeline_per_s2", 1), ("sql_to_s2", 1), ("mql_to_sql", 1),
                                  ("conv_to_mql", 1), ("cvr", 1), ("cpc", -1)], "higher_is_better": True},
    "won_roas": {"factors": [("deal_value", 1), ("s2_to_won", 1), ("sql_to_s2", 1), ("mql_to_sql", 1),
                             ("conv_to_mql", 1), ("cvr", 1), ("cpc", -1)], "higher_is_better": True},
}

LABELS = {
    "impressions": "impressions", "ctr": "click-through rate", "cvr": "click to conversion rate",
    "cpc": "CPC", "conv_to_mql": "conversion to MQL rate", "mql_to_sql": "MQL to SQL rate",
    "sql_to_s2": "SQL to S2 rate", "s2_to_won": "S2 to won rate", "pipeline_per_s2": "pipeline per S2",
    "deal_value": "deal size", "value_per_conversion": "value per conversion",
    "cpa": "CPA", "cost_per_s2": "Cost per S2", "cost_per_won": "Cost per won deal",
    "roas": "ROAS", "pipeline_roas": "Pipeline ROAS", "won_roas": "Closed-won ROAS",
    "conversions": "Conversions", "s2s": "S2s", "won": "Won deals", "pipeline": "Pipeline",
    "won_value": "Closed-won revenue",
}

# Volume behind each rate: a rate is only trusted when its denominator passes the gate.
DENOMINATOR = {"ctr": "impressions", "cvr": "clicks", "cpc": "clicks", "conv_to_mql": "conversions",
               "mql_to_sql": "mqls", "sql_to_s2": "sqls", "s2_to_won": "s2s",
               "pipeline_per_s2": "s2s", "deal_value": "won", "value_per_conversion": "conversions"}
