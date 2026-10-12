def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_create_user(client):
    result = client.post("/users/", json={"email": "alice@test.com", "password": "AlicePass1!"})
    assert result.status_code == 201
    assert result.json()["email"] == "alice@test.com"
    assert "hashed_password" not in result.json()
    assert result.json()["is_superuser"] is False


def test_create_user_password_too_short(client):
    assert client.post("/users/", json={"email": "short@test.com", "password": "short"}).status_code == 422


def test_duplicate_user(client):
    body = {"email": "dup@test.com", "password": "DupPass1234!"}
    assert client.post("/users/", json=body).status_code == 201
    assert client.post("/users/", json=body).status_code == 400


def test_list_users(client, admin_headers):
    assert client.get("/users/", headers=admin_headers).status_code == 200


def test_user_not_found(client, admin_headers):
    assert client.get("/users/99999", headers=admin_headers).status_code == 404
