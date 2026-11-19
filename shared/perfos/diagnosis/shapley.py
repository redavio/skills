"""Shapley split of a gap across factors of a multiplicative formula.

KPI = product of factor ** exponent (exponent +1 or -1). CPA = CPC^1 x CVR^-1, ROAS =
value_per_conversion x CVR x CPC^-1, S2s = impressions x CTR x CVR x ... .
Each factor's share is its average marginal effect over every order of switching factors
from baseline to actual. Shares sum exactly to the gap; no leftover, no order bias.
Coalition formula: 2^n evaluations, fine for funnels up to ~15 factors.
"""
from __future__ import annotations

from itertools import combinations
from math import factorial


def kpi_value(factors: list[tuple[str, int]], values: dict) -> float:
    out = 1.0
    for name, exp in factors:
        out *= values[name] ** exp
    return out


def split(factors: list[tuple[str, int]], actual: dict, base: dict) -> dict | None:
    """Return {"base", "actual", "gap", "drivers": [{factor, base, actual, contribution, share}]}.

    None if any factor is missing or zero where it is divided by (can't be split honestly).
    """
    names = [n for n, _ in factors]
    for n, exp in factors:
        for src in (actual, base):
            v = src.get(n)
            if v is None or (exp < 0 and v == 0):
                return None
    n = len(names)
    base_kpi = kpi_value(factors, base)
    act_kpi = kpi_value(factors, actual)
    gap = act_kpi - base_kpi

    cache: dict = {}

    def v(subset: frozenset) -> float:
        if subset not in cache:
            cache[subset] = kpi_value(factors, {k: (actual[k] if k in subset else base[k]) for k in names})
        return cache[subset]

    drivers = []
    for name in names:
        others = [x for x in names if x != name]
        phi = 0.0
        for size in range(len(others) + 1):
            w = factorial(size) * factorial(n - size - 1) / factorial(n)
            for coal in combinations(others, size):
                s = frozenset(coal)
                phi += w * (v(s | {name}) - v(s))
        drivers.append({"factor": name, "base": base[name], "actual": actual[name],
                        "contribution": phi, "share": (phi / gap) if gap else 0.0})
    return {"base": base_kpi, "actual": act_kpi, "gap": gap, "drivers": drivers}
