import sys
sys.path.insert(0, ".")
from app.core.experiment import Experiment, ExperimentEngine, ExperimentStatus
from datetime import datetime, timezone, timedelta

def test_experiment_profit():
    e = Experiment(name="Test", hypothesis="H", budget=100)
    e.add_cost(40)
    e.add_revenue(120)
    assert e.profit == 80
    assert e.roi == 2.0
    assert e.margin == 80/120

def test_experiment_transition():
    e = Experiment(name="T", hypothesis="H")
    assert e.status == ExperimentStatus.IDEA
    e.transition(ExperimentStatus.VALIDATING, "test")
    assert e.status == ExperimentStatus.VALIDATING
    assert len(e.learnings) == 1

def test_experiment_evaluate_winner():
    e = Experiment(name="T", hypothesis="H", budget=50)
    e.status = ExperimentStatus.LIVE
    e.add_cost(50)
    e.add_revenue(200)  # roi 3, profit 150 -> winner
    old = e.status
    e.evaluate()
    assert e.status == ExperimentStatus.WINNER

def test_experiment_evaluate_failed():
    e = Experiment(name="T", hypothesis="H", budget=10, deadline_days=-1)  # already past
    e.status = ExperimentStatus.LIVE
    e.add_cost(20)
    e.evaluate()
    # deadline past and profit 0 -> failed or paused
    assert e.status in [ExperimentStatus.FAILED, ExperimentStatus.PAUSED]

def test_engine():
    eng = ExperimentEngine()
    e = eng.create(name="E1", hypothesis="H")
    assert eng.get(e.id) == e
    assert len(eng.list()) == 1
    stats = eng.stats()
    assert stats["total"] == 1
    assert stats["by_status"]["IDEA"] == 1

if __name__ == "__main__":
    test_experiment_profit()
    test_experiment_transition()
    test_experiment_evaluate_winner()
    test_experiment_evaluate_failed()
    test_engine()
    print("✅ test_experiment passed")
