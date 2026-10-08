from app.tests.conftest import auth_headers


def test_upload_integrity_timeline_and_citations(client, token):
    case = client.post(
        "/cases",
        headers=auth_headers(token),
        json={"title": "Case Beta", "description": "Synthetic"},
    ).json()

    upload = client.post(
        f"/cases/{case['id']}/evidence",
        headers=auth_headers(token),
        files={"file": ("note.txt", b"vehicle at 10pm near warehouse", "text/plain")},
    )
    assert upload.status_code == 201
    evidence = upload.json()["evidence"]
    observations = upload.json()["observations"]
    assert observations

    integrity = client.get(
        f"/cases/{case['id']}/evidence/{evidence['id']}/integrity",
        headers=auth_headers(token),
    )
    assert integrity.status_code == 200
    assert integrity.json()["matches"] is True

    timeline = client.get(f"/cases/{case['id']}/evidence/timeline", headers=auth_headers(token))
    assert timeline.status_code == 200
    assert len(timeline.json()["events"]) >= 1

    query = client.post(
        f"/cases/{case['id']}/investigation/query",
        headers=auth_headers(token),
        json={"question": "What mentions vehicle?"},
    )
    assert query.status_code == 200
    assert query.json()["result"]["citations"]


def test_upload_validation_size_limit(client, token):
    case = client.post(
        "/cases",
        headers=auth_headers(token),
        json={"title": "Case Gamma", "description": "Synthetic"},
    ).json()

    huge = b"a" * (1024 * 1024 + 100)
    upload = client.post(
        f"/cases/{case['id']}/evidence",
        headers=auth_headers(token),
        files={"file": ("huge.bin", huge, "application/octet-stream")},
    )
    assert upload.status_code == 400
    assert "max upload size" in upload.json()["detail"].lower()


def test_insufficient_evidence_behavior(client, token):
    case = client.post(
        "/cases",
        headers=auth_headers(token),
        json={"title": "Case Delta", "description": "Synthetic"},
    ).json()

    response = client.post(
        f"/cases/{case['id']}/investigation/query",
        headers=auth_headers(token),
        json={"question": "Who is guilty?"},
    )
    assert response.status_code == 200
    assert "Insufficient evidence" in response.json()["result"]["answer"]
    assert response.json()["result"]["citations"] == []
