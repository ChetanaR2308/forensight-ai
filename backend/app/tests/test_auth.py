from app.tests.conftest import auth_headers


def test_auth_success(client):
    response = client.post("/auth/token", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_auth_failure(client):
    response = client.post("/auth/token", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_case_requires_auth(client):
    response = client.get("/cases")
    assert response.status_code == 401
