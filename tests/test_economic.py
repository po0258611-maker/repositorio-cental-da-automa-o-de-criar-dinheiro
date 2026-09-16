import sys
sys.path.insert(0, ".")
from app.core.economic import EconomicEngine, SurvivalMode

def test_profit_margin():
    e = EconomicEngine(initial_balance=1000, burn_rate_daily=10)
    e.record_revenue(1000, "Sale")
    e.record_expense(300, "Cost")
    assert e.profit == 700
    assert abs(e.margin - 0.7) < 0.01
    assert e.roi(300) == 700/300

def test_runway():
    e = EconomicEngine(initial_balance=100, burn_rate_daily=10)
    assert e.runway_days == 10
    e.survival_threshold_days = 7
    e.emergency_threshold_days = 3
    e.balance = 50  # 5 days -> survival
    e._update_mode()
    assert e.mode == SurvivalMode.SURVIVAL
    e.balance = 20  # 2 days -> emergency
    e._update_mode()
    assert e.mode == SurvivalMode.EMERGENCY
    e.balance = 5  # 0.5 days -> emergency
    e._update_mode()
    assert e.mode == SurvivalMode.EMERGENCY

def test_survival_modes():
    e = EconomicEngine(initial_balance=1000, burn_rate_daily=5)
    e.revenue_total = 2000
    e.expenses_total = 500
    e._update_mode()
    assert e.mode == SurvivalMode.GROW
    e.expenses_total = 1900
    e._update_mode()
    # margin 0.05 -> NORMAL
    assert e.mode == SurvivalMode.NORMAL

def test_cac_ltv_roas():
    e = EconomicEngine()
    assert e.calculate_cac(200, 10) == 20
    assert e.calculate_cac(200, 0) == 0
    ltv = e.calculate_ltv(100, 1, 0.5, 12)
    assert ltv == 600
    assert e.calculate_roas(1000, 200) == 5
    assert e.calculate_roas(1000, 0) == 0

if __name__ == "__main__":
    test_profit_margin()
    test_runway()
    test_survival_modes()
    test_cac_ltv_roas()
    print("✅ test_economic passed")
