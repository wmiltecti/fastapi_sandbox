from fastapi.testclient import TestClient
import importlib

# Garante que carregamos o app definido em main.py
main = importlib.import_module("main")
client = TestClient(main.app)

def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"
