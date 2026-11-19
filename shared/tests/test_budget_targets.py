from datetime import date, timedelta

import pytest

from perfos import budget, targets

END = date(2026, 10, 31)


def _daily(days, cost, clicks, conv, s2s, pipeline):
    return {END - timedelta(days=i): {"cost": cost, "clicks": clicks, "conversions": conv,
                                      "mqls": conv, "sqls": conv, "s2s": s2s, "pipeline": pipeline}
            for i in range(days)}


def test_capped_winner_gets_capped_increase():
    c = budget.Campaign("1", "search|nonbrand|x|us|en", "nonbrand", current_budget=100, target=5.0,
                        daily=_daily(30, 100, 50, 3, 1, 1000), lost_is_budget=0.4, impression_share=0.5)
    r = budget.decide(c, END)
    assert r["direction"] == "increase"
    assert r["change_pct"] <= 0.20 + 1e-9


def test_uncapped_winner_gets_nothing():
    c = budget.Campaign("1", "n", "nonbrand", 100, 5.0, _daily(30, 100, 50, 3, 1, 1000),
                        lost_is_budget=0.0, impression_share=0.9)
    assert budget.decide(c, END) is None


def test_brand_never_budgeted_on_roas():
    c = budget.Campaign("1", "b", "brand", 100, 5.0, _daily(30, 100, 50, 3, 1, 1000), lost_is_budget=0.4,
                        impression_share=0.5)
    assert budget.decide(c, END) is None


def test_zero_return_burner_is_cut():
    c = budget.Campaign("1", "n", "nonbrand", 100, 5.0, _daily(30, 100, 50, 1, 0, 0), lost_is_budget=0.3,
                        impression_share=0.5)
    r = budget.decide(c, END)
    assert r["direction"] == "decrease"


def test_target_math():
    r = targets.recommend(ltv=60000, ltv_to_cac=3, s2_to_won=0.25, conv_to_s2=0.10,
                          weekly_conversions=[10, 12, 9, 15, 11], weekly_s2s=[1, 1.2, 0.9, 1.5, 1.1])
    assert r["max_cac"] == pytest.approx(20000)
    assert r["max_cost_per_s2"] == pytest.approx(5000)
    assert r["tcpa"] == pytest.approx(500)
    assert r["trusted"] is True


def test_window_never_reaches_past_data():
    c = budget.Campaign("1", "n", "nonbrand", 100, 5.0, _daily(30, 100, 50, 1, 0, 0), lost_is_budget=0.3,
                        impression_share=0.5)
    r = budget.decide(c, END)
    assert r["window_days"] == 30
    assert r["recommended_budget"] == pytest.approx(25.0)  # 25% of $100 average daily spend
