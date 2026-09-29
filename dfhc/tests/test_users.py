from datetime import timedelta

from jose import jwt


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_user_requires_auth(client):
    r = client.post("/users/", json={"email": "anon@test.com", "password": "AnonPass1234!"})
    assert r.status_code == 401


def test_create_user_as_admin(client, admin_headers):
    r = client.post("/users/", json={"email": "alice@test.com", "password": "AlicePass1!"}, headers=admin_headers)
    assert r.status_code == 201
    assert r.json()["email"] == "alice@test.com"
    assert r.json()["is_superuser"] is False


def test_staff_cannot_manage_users(client, make_staff):
    headers = make_staff("staff-nomanage@test.com")
    assert client.get("/users/", headers=headers).status_code == 403
    r = client.post("/users/", json={"email": "x@test.com", "password": "XPass123456"}, headers=headers)
    assert r.status_code == 403


def test_read_me(client, make_staff):
    headers = make_staff("me@test.com")
    r = client.get("/users/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == "me@test.com"


def test_create_user_password_too_short(client, admin_headers):
    r = client.post("/users/", json={"email": "short@test.com", "password": "short"}, headers=admin_headers)
    assert r.status_code == 422


def test_update_user_password_too_short(client, admin_headers):
    r = client.post("/users/", json={"email": "upd@test.com", "password": "UpdPass12345"}, headers=admin_headers)
    user_id = r.json()["id"]
    r = client.patch(f"/users/{user_id}", json={"password": "short"}, headers=admin_headers)
    assert r.status_code == 422


def test_duplicate_user(client, admin_headers):
    client.post("/users/", json={"email": "dup@test.com", "password": "DupPass1234!"}, headers=admin_headers)
    r = client.post("/users/", json={"email": "dup@test.com", "password": "DupPass1234!"}, headers=admin_headers)
    assert r.status_code == 400


def test_list_users(client, admin_headers):
    r = client.get("/users/", headers=admin_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_users_requires_auth(client):
    assert client.get("/users/").status_code == 401


def test_user_not_found(client, admin_headers):
    r = client.get("/users/99999", headers=admin_headers)
    assert r.status_code == 404


def test_inactive_user_rejected(client, admin_headers):
    r = client.post("/users/", json={"email": "gone@test.com", "password": "GonePass12345"}, headers=admin_headers)
    user_id = r.json()["id"]
    token = client.post("/auth/token", data={"username": "gone@test.com", "password": "GonePass12345"}).json()
    client.patch(f"/users/{user_id}", json={"is_active": False}, headers=admin_headers)
    r = client.get("/users/me", headers={"Authorization": f"Bearer {token['access_token']}"})
    assert r.status_code == 403


def test_token_signed_with_old_hardcoded_key_is_rejected(client, admin_headers):
    """Regression: security.py used to sign tokens with a hardcoded key."""
    from datetime import datetime, timezone

    forged = jwt.encode(
        {"sub": "admin@dfhc.test", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "change-me-in-production",
        algorithm="HS256",
    )
    r = client.get("/users/", headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 401
