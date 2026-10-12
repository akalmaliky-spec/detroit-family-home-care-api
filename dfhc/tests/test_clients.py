CLIENT_PAYLOAD = {
    "full_name": "Mary Johnson",
    "date_of_birth": "1980-05-15",
    "diagnosis": "Cerebral Palsy",
    "address": "123 Main St, Detroit, MI 48201",
    "phone": "313-555-1234",
    "emergency_contact_name": "James Johnson",
    "emergency_contact_phone": "313-555-5678",
    "medicaid_id": "MI12345678",
    "is_active": True,
    "notes": "Requires wheelchair access",
}


def test_clients_requires_auth(client, admin_headers):
    r = client.get("/clients/")
    assert r.status_code == 401


def test_create_client(client, admin_headers):
    r = client.post("/clients/", json=CLIENT_PAYLOAD, headers=admin_headers)
    assert r.status_code == 201
    data = r.json()
    assert data["full_name"] == "Mary Johnson"
    assert data["id"] is not None
    assert data["date_of_birth"] == "1980-05-15"


def test_list_clients(client, admin_headers):
    headers = admin_headers
    r = client.get("/clients/", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_client_not_found(client, admin_headers):
    r = client.get("/clients/99999", headers=admin_headers)
    assert r.status_code == 404
    assert r.json()["detail"] == "Client not found"


def test_get_client_by_id(client, admin_headers):
    headers = admin_headers
    create_r = client.post("/clients/", json={**CLIENT_PAYLOAD, "full_name": "Test Client"}, headers=headers)
    assert create_r.status_code == 201
    client_id = create_r.json()["id"]
    r = client.get(f"/clients/{client_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["full_name"] == "Test Client"


def test_update_client(client, admin_headers):
    headers = admin_headers
    create_r = client.post("/clients/", json={**CLIENT_PAYLOAD, "full_name": "Update Me"}, headers=headers)
    client_id = create_r.json()["id"]
    r = client.patch(f"/clients/{client_id}", json={"full_name": "Updated Name"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["full_name"] == "Updated Name"


def test_partial_update_client_notes_only_preserves_other_fields(client, admin_headers):
    headers = admin_headers
    create_payload = {**CLIENT_PAYLOAD, "full_name": "Partial Update", "notes": "Old notes", "is_active": True}
    create_r = client.post("/clients/", json=create_payload, headers=headers)
    client_id = create_r.json()["id"]
    patch_r = client.patch(f"/clients/{client_id}", json={"notes": "Updated notes"}, headers=headers)
    assert patch_r.status_code == 200
    patched = patch_r.json()
    assert patched["notes"] == "Updated notes"
    assert patched["full_name"] == "Partial Update"
    assert patched["is_active"] is True


def test_update_nonexistent_client_returns_404(client, admin_headers):
    headers = admin_headers
    patch_r = client.patch("/clients/999999", json={"full_name": "Does Not Matter"}, headers=headers)
    assert patch_r.status_code == 404
    assert patch_r.json()["detail"] == "Client not found"


def test_delete_client(client, admin_headers):
    headers = admin_headers
    create_r = client.post("/clients/", json={**CLIENT_PAYLOAD, "full_name": "Delete Me"}, headers=headers)
    client_id = create_r.json()["id"]
    r = client.delete(f"/clients/{client_id}", headers=headers)
    assert r.status_code == 204
    r2 = client.get(f"/clients/{client_id}", headers=headers)
    assert r2.status_code == 404


def test_delete_nonexistent_client_returns_404(client, admin_headers):
    headers = admin_headers
    r = client.delete("/clients/999999", headers=headers)
    assert r.status_code == 404
    assert r.json()["detail"] == "Client not found"


def test_create_client_missing_full_name_returns_422(client, admin_headers):
    headers = admin_headers
    payload = CLIENT_PAYLOAD.copy()
    payload.pop("full_name")
    response = client.post("/clients/", json=payload, headers=headers)
    assert response.status_code == 422


def test_create_client_invalid_date_of_birth_returns_422(client, admin_headers):
    headers = admin_headers
    payload = CLIENT_PAYLOAD.copy()
    payload["date_of_birth"] = "not-a-date"
    response = client.post("/clients/", json=payload, headers=headers)
    assert response.status_code == 422
