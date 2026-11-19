import random

import pytest

from perfos.diagnosis import chains, shapley


def test_two_factor_matches_known_split():
    # CPA = CPC / CVR. Base CPC 2, CVR 0.05 -> 40. Actual CPC 2.2, CVR 0.04 -> 55.
    r = shapley.split([("cpc", 1), ("cvr", -1)], {"cpc": 2.2, "cvr": 0.04}, {"cpc": 2.0, "cvr": 0.05})
    assert r["base"] == pytest.approx(40)
    assert r["actual"] == pytest.approx(55)
    by = {d["factor"]: d["contribution"] for d in r["drivers"]}
    # midpoint (2-player Shapley): cpc = ((44-40)+(55-50))/2 = 4.5, cvr = ((50-40)+(55-44))/2 = 10.5
    assert by["cpc"] == pytest.approx(4.5)
    assert by["cvr"] == pytest.approx(10.5)


@pytest.mark.parametrize("kpi", list(chains.CHAINS))
def test_shares_always_sum_to_one(kpi):
    rng = random.Random(kpi)
    facs = chains.CHAINS[kpi]["factors"]
    for _ in range(20):
        base = {n: rng.uniform(0.5, 2.0) for n, _ in facs}
        act = {n: v * rng.uniform(0.6, 1.5) for n, v in base.items()}
        r = shapley.split(facs, act, base)
        assert sum(d["contribution"] for d in r["drivers"]) == pytest.approx(r["gap"], rel=1e-9, abs=1e-12)
        assert sum(d["share"] for d in r["drivers"]) == pytest.approx(1.0)


def test_unmoved_factor_gets_nothing():
    facs = chains.CHAINS["s2s"]["factors"]
    base = {n: 1.0 for n, _ in facs}
    act = dict(base, cvr=0.8)
    r = shapley.split(facs, act, base)
    by = {d["factor"]: d["share"] for d in r["drivers"]}
    assert by["cvr"] == pytest.approx(1.0)
    assert all(abs(v) < 1e-12 for k, v in by.items() if k != "cvr")


def test_missing_or_zero_divisor_refuses():
    assert shapley.split([("cpc", 1), ("cvr", -1)], {"cpc": 2, "cvr": 0}, {"cpc": 2, "cvr": 0.05}) is None
    assert shapley.split([("cpc", 1)], {}, {"cpc": 1}) is None
