import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
import app.container as container_module


@pytest.fixture
def client(tmp_path):
    settings.uploads_dir = str(tmp_path / "uploads")
    settings.max_upload_size_mb = 1
    settings.enable_llm = False
    container_module._container = None
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def token(client: TestClient):
    response = client.post(
        "/auth/token",
        json={"username": "investigator", "password": settings.demo_investigator_password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": "Bearer " + token}
