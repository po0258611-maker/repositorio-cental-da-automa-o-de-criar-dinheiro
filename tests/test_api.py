import sys
sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] in ["healthy", "degraded"]

def test_agents_list():
    r = client.get("/agents")
    assert r.status_code == 200
    assert r.json()["total"] >= 20
    assert "market_agent" in [a["name"] for a in r.json()["agents"]]

def test_experiments_crud():
    r = client.post("/experiments", json={"name":"Test API","hypothesis":"H API","budget":10})
    assert r.status_code == 200
    exp_id = r.json()["id"]
    r2 = client.get(f"/experiments/{exp_id}")
    assert r2.status_code == 200
    assert r2.json()["name"] == "Test API"
    # update
    r3 = client.patch(f"/experiments/{exp_id}", json={"cost": 5})
    assert r3.status_code == 200
    assert r3.json()["cost"] == 5

def test_finance():
    r = client.get("/finance/dashboard")
    assert r.status_code == 200
    assert "balance" in r.json()
    r2 = client.post("/finance/revenue", json={"amount": 100, "description":"Test"})
    assert r2.status_code == 200
    assert r2.json()["transaction"]["amount"] == 100

def test_products():
    r = client.post("/products", json={"name":"Produto Teste API","price":47})
    assert r.status_code == 200
    pid = r.json()["id"]
    r2 = client.get(f"/products/{pid}")
    assert r2.status_code == 200

def test_memory():
    r = client.post("/memory", json={"category":"market_memory","action":"test","result":"ok","lesson":"learn"})
    assert r.status_code == 200
    r2 = client.get("/memory")
    assert r2.status_code == 200
    assert r2.json()["stats"]["total"] >= 1

def test_orchestrator():
    r = client.get("/agents/orchestrator/status")
    assert r.status_code == 200
    assert "cycle_count" in r.json()

if __name__ == "__main__":
    test_health()
    print("✓ health")
    test_agents_list()
    print("✓ agents")
    test_experiments_crud()
    print("✓ experiments")
    test_finance()
    print("✓ finance")
    test_products()
    print("✓ products")
    test_memory()
    print("✓ memory")
    test_orchestrator()
    print("✓ orchestrator")
    print("✅ test_api passed")
