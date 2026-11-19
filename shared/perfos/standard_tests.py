"""Standard test library: run for every client (actions/tests.md).

Source: standards/README.md backlog tests. Add here when the playbook adds one.
ICE is a starting estimate (1-10 each) until the client's own data rescores it.
"""
STANDARD_TESTS = [
    {"hypothesis": "Search partners on lowers cost per S2 without hurting lead quality",
     "goal_metric": "cost_per_s2", "segment": "nonbrand", "impact": 5, "confidence": 4, "ease": 9},
    {"hypothesis": "Target impression share bidding on brand holds coverage at lower cost",
     "goal_metric": "impression_share", "segment": "brand", "impact": 4, "confidence": 5, "ease": 9},
    {"hypothesis": "Smart Bidding Exploration (ROAS tolerance 5 to 30%) finds new converting queries",
     "goal_metric": "pipeline_roas", "segment": "nonbrand", "impact": 6, "confidence": 4, "ease": 8},
    {"hypothesis": "Journey-Aware Bidding (target CPA path) beats the value path on pipeline",
     "goal_metric": "pipeline_roas", "segment": "nonbrand", "impact": 6, "confidence": 4, "ease": 7},
    {"hypothesis": "AI Max on non-brand adds qualified volume at or under goal cost per S2",
     "goal_metric": "cost_per_s2", "segment": "nonbrand", "impact": 8, "confidence": 5, "ease": 7},
    {"hypothesis": "AI Max on brand and competitor, once non-brand proves out",
     "goal_metric": "cost_per_s2", "segment": "competitor", "impact": 5, "confidence": 4, "ease": 7},
    {"hypothesis": "Bing broad match plus LinkedIn targeting on named companies and roles lowers cost per qualified lead",
     "goal_metric": "cost_per_s2", "segment": "nonbrand", "impact": 6, "confidence": 4, "ease": 6},
]
