import pytest

from perfos.diagnosis import mix


def test_pure_mix_shift():
    # each segment's CPA unchanged; conversions shift toward the pricier segment
    base = {"brand": {"cost": 400, "conversions": 20}, "nonbrand": {"cost": 1600, "conversions": 8}}
    act = {"brand": {"cost": 200, "conversions": 10}, "nonbrand": {"cost": 3600, "conversions": 18}}
    r = mix.split(act, base, "cost", "conversions")
    assert r["rate_effect"] == pytest.approx(0, abs=1e-9)
    assert r["mix_share"] == pytest.approx(1.0)


def test_rate_plus_mix_equals_total_change():
    base = {"a": {"cost": 500, "conversions": 10}, "b": {"cost": 900, "conversions": 5}}
    act = {"a": {"cost": 700, "conversions": 12}, "b": {"cost": 800, "conversions": 3}}
    r = mix.split(act, base, "cost", "conversions")
    kpi = lambda s: sum(x["cost"] for x in s.values()) / sum(x["conversions"] for x in s.values())
    assert r["total"] == pytest.approx(kpi(act) - kpi(base))
