from fastapi.testclient import TestClient
import importlib
import types

main = importlib.import_module("main")
client = TestClient(main.app)

def test_login_ok(monkeypatch):
    # Simula um usuário encontrado no DB
    def fake_find_user(login: str):
        return {
            "id": 1,
            "nome": "Fulano Tester",
            "perfil": "ADMIN",
            "tipo": "CPF",
            "cpf": "12345678900",
            "senha": "minhasenha",
            "senha_hash": None,
        }

    def fake_verify_password(input_password: str, row: dict) -> bool:
        return input_password == "minhasenha"

    monkeypatch.setattr(main, "find_user_in_db", fake_find_user)
    monkeypatch.setattr(main, "verify_password", fake_verify_password)

    resp = client.post(
        "/auth/login",
        json={"login": "123.456.789-00", "senha": "minhasenha"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["nome"] == "Fulano Tester"
    assert data["perfil"] == "ADMIN"
    assert data["userId"] == "1"

def test_login_credenciais_invalidas(monkeypatch):
    # Simula usuário não encontrado
    def fake_find_user(login: str):
        return None

    monkeypatch.setattr(main, "find_user_in_db", fake_find_user)

    resp = client.post(
        "/auth/login",
        json={"login": "000.000.000-00", "senha": "qualquer"},
    )
    assert resp.status_code == 401
