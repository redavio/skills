"""Mix vs rate: did the total move because spend shifted between segments, or because the
segments themselves got better or worse? (actions/diagnosis.md step 2)

KPI = sum(numerator) / sum(denominator), e.g. CPA = cost / conversions.
Written as sum(w_i x r_i) with w_i = denominator share and r_i = segment rate.
Split with midpoint weights, which is exact (the 2-player Shapley split):
  rate effect = sum(avg w x change in r), mix effect = sum(avg r x change in w).
"""
from __future__ import annotations


def split(actual: dict, base: dict, numerator: str, denominator: str) -> dict | None:
    """actual/base: {segment: {numerator: x, denominator: y}}. Segments missing on one side
    count as zero there."""
    segs = set(actual) | set(base)

    def wr(side):
        tot = sum(side.get(s, {}).get(denominator, 0) for s in segs)
        if not tot:
            return None
        out = {}
        for s in segs:
            num = side.get(s, {}).get(numerator, 0)
            den = side.get(s, {}).get(denominator, 0)
            out[s] = (den / tot, (num / den) if den else None)
        return out

    a, b = wr(actual), wr(base)
    if a is None or b is None:
        return None
    rate = mix = 0.0
    per = {}
    for s in segs:
        w1, r1 = a[s]
        w0, r0 = b[s]
        # a segment that is new or gone has no rate on one side: use its other-side rate
        r1 = r1 if r1 is not None else r0
        r0 = r0 if r0 is not None else r1
        if r1 is None:
            continue
        re = (w0 + w1) / 2 * (r1 - r0)
        me = (r0 + r1) / 2 * (w1 - w0)
        rate += re
        mix += me
        per[s] = {"rate_effect": re, "mix_effect": me}
    total = rate + mix
    return {"rate_effect": rate, "mix_effect": mix, "total": total,
            "mix_share": (mix / total) if total else 0.0, "by_segment": per}
