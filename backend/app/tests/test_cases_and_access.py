from app.tests.conftest import auth_headers


def test_case_crud_and_access_control(client, token):
    create = client.post(
        "/cases",
        headers=auth_headers(token),
        json={"title": "Case Alpha", "description": "Synthetic test case"},
    )
    assert create.status_code == 201
    case_id = create.json()["id"]

    get_ok = client.get(f"/cases/{case_id}", headers=auth_headers(token))
    assert get_ok.status_code == 200

    analyst = client.post("/auth/token", json={"username": "analyst", "password": "analyst123"})
    analyst_token = analyst.json()["access_token"]
    denied = client.get(f"/cases/{case_id}", headers=auth_headers(analyst_token))
    assert denied.status_code == 403

    update = client.patch(
        f"/cases/{case_id}", headers=auth_headers(token), json={"description": "Updated"}
    )
    assert update.status_code == 200
    assert update.json()["description"] == "Updated"
