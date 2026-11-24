import pytest
from fastapi.testclient import TestClient

from app.db.store import MemoryStore, get_store
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_memory_store() -> None:
    store = get_store()
    if isinstance(store, MemoryStore):
        store.reset()


def _login_headers(username: str = "karyawan", password: str = "moolagi123") -> dict[str, str]:
    resp = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "moolagi-backend"
    assert body["storage_mode"] == "memory"


def test_login_valid_and_me():
    resp = client.post("/api/v1/auth/login", json={"username": "karyawan", "password": "moolagi123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "karyawan"

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {data['access_token']}"})
    assert me.status_code == 200
    assert me.json()["username"] == "karyawan"


def test_login_wrong_password_rejected():
    resp = client.post("/api/v1/auth/login", json={"username": "karyawan", "password": "salah"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_empty_fields_rejected():
    resp = client.post("/api/v1/auth/login", json={"username": "", "password": ""})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_protected_endpoints_require_login():
    assert client.get("/api/v1/ingredients").status_code == 401
    assert client.get("/api/v1/stocks/history").status_code == 401
    assert (
        client.post(
            "/api/v1/stocks/closing",
            json={"log_date": "2026-11-22", "items": [{"ingredient_id": "ING-ESKRIM", "closing_stock": 10}]},
        ).status_code
        == 401
    )


def test_list_ingredients_returns_assumptions():
    headers = _login_headers("karyawan")
    resp = client.get("/api/v1/ingredients", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 5
    assert all(item["is_assumption"] is True for item in body["items"])


def test_record_closing_stock_valid_and_in_history():
    headers = _login_headers("karyawan")
    before = client.get("/api/v1/stocks/history", headers=headers).json()["total"]

    payload = {
        "log_date": "2026-11-22",
        "items": [
            {"ingredient_id": "ING-ESKRIM", "closing_stock": 18.0, "notes": "Closing sore"},
            {"ingredient_id": "ING-SUSU", "closing_stock": 11.5},
        ],
    }
    resp = client.post("/api/v1/stocks/closing", json=payload, headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["saved_count"] == 2
    assert body["records"][0]["recorded_by"] == "karyawan"

    after = client.get("/api/v1/stocks/history", headers=headers).json()
    assert after["total"] == before + 2
    latest_eskrim = client.get(
        "/api/v1/stocks/history?ingredient_id=ING-ESKRIM", headers=headers
    ).json()["items"][0]
    assert latest_eskrim["closing_stock"] == 18.0


def test_record_closing_stock_negative_rejected_without_saving():
    headers = _login_headers("karyawan")
    before = client.get("/api/v1/stocks/history", headers=headers).json()["total"]

    payload = {
        "log_date": "2026-11-22",
        "items": [
            {"ingredient_id": "ING-ESKRIM", "closing_stock": -3},
        ],
    }
    resp = client.post("/api/v1/stocks/closing", json=payload, headers=headers)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
    assert "negatif" in resp.json()["error"]["message"].lower()

    after = client.get("/api/v1/stocks/history", headers=headers).json()["total"]
    assert after == before


def test_record_closing_stock_missing_value_rejected_without_saving():
    headers = _login_headers("karyawan")
    before = client.get("/api/v1/stocks/history", headers=headers).json()["total"]

    payload = {
        "log_date": "2026-11-22",
        "items": [
            {"ingredient_id": "ING-ESKRIM", "closing_stock": None},
        ],
    }
    resp = client.post("/api/v1/stocks/closing", json=payload, headers=headers)
    assert resp.status_code == 422
    assert client.get("/api/v1/stocks/history", headers=headers).json()["total"] == before


def test_record_closing_stock_unknown_ingredient_is_atomic():
    headers = _login_headers("karyawan")
    before = client.get("/api/v1/stocks/history", headers=headers).json()["total"]

    payload = {
        "log_date": "2026-11-22",
        "items": [
            {"ingredient_id": "ING-ESKRIM", "closing_stock": 15.0},
            {"ingredient_id": "ING-TIDAK-ADA", "closing_stock": 5.0},
        ],
    }
    resp = client.post("/api/v1/stocks/closing", json=payload, headers=headers)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "INGREDIENT_NOT_FOUND"
    # Tidak boleh ada partial write untuk ING-ESKRIM
    assert client.get("/api/v1/stocks/history", headers=headers).json()["total"] == before
