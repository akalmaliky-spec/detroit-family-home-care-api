from datetime import datetime, timedelta, timezone
import os
import subprocess
import sys
import pytest
from jose import jwt
from dfhc.app.core.config import SECRET_KEY
from dfhc.app.core.security import decode_access_token, refresh_token_hash, verify_password
from dfhc.app.core.rate_limit import AuthRateLimiter
from dfhc.app.models import RefreshSession, User
from starlette.requests import Request

PASSWORD = "StrongPass123!"


def account(client, email="member@test.com"):
    created = client.post("/users/", json={"email": email, "password": PASSWORD})
    assert created.status_code == 201
    login = client.post("/auth/token", data={"username": email, "password": PASSWORD})
    assert login.status_code == 200
    return created.json(), login.json()


def headers(tokens):
    return {"Authorization": "Bearer " + tokens["access_token"]}


@pytest.mark.parametrize("method,path", [("get", "/users/"), ("get", "/users/1"), ("patch", "/users/1"), ("delete", "/users/1")])
def test_user_administration_requires_auth(client, method, path):
    assert getattr(client, method)(path).status_code == 401


@pytest.mark.parametrize("method,path", [("get", "/users/"), ("get", "/users/1"), ("patch", "/users/1"), ("delete", "/users/1")])
def test_regular_member_cannot_administer_users(client, method, path):
    _, tokens = account(client)
    assert getattr(client, method)(path, headers=headers(tokens)).status_code == 403


def test_hashing_and_configured_signing_key(client, db):
    user, tokens = account(client)
    stored = db.get(User, user["id"])
    assert stored.hashed_password != PASSWORD
    assert verify_password(PASSWORD, stored.hashed_password)
    claims = jwt.decode(tokens["access_token"], SECRET_KEY, algorithms=["HS256"])
    assert claims["sub"] == str(user["id"])
    assert claims["token_type"] == "access"
    session = db.get(RefreshSession, refresh_token_hash(tokens["refresh_token"]))
    assert session is not None and session.token_hash != tokens["refresh_token"]
    assert client.get("/users/me", headers=headers(tokens)).status_code == 200


def test_wrong_signing_key_and_missing_claims_fail_closed(client):
    user, tokens = account(client)
    payload = {"sub": str(user["id"]), "ver": 0, "token_type": "access", "iat": int(datetime.now(timezone.utc).timestamp()), "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp())}
    forged = jwt.encode(payload, "another-generated-secret-that-is-long-enough", algorithm="HS256")
    assert client.get("/users/me", headers={"Authorization": "Bearer " + forged}).status_code == 401
    for missing in ("exp", "iat", "sub", "ver", "token_type"):
        incomplete = {k: v for k, v in payload.items() if k != missing}
        assert decode_access_token(jwt.encode(incomplete, SECRET_KEY, algorithm="HS256")) is None
    assert client.get("/users/me", headers={"Authorization": "Bearer " + tokens["refresh_token"]}).status_code == 401


def test_expired_access_token_rejected(client):
    user, _ = account(client)
    token = jwt.encode({"sub": str(user["id"]), "ver": 0, "token_type": "access", "iat": 1, "exp": 2}, SECRET_KEY, algorithm="HS256")
    assert client.get("/users/me", headers={"Authorization": "Bearer " + token}).status_code == 401


def test_refresh_rotates_and_rejects_replay(client):
    _, tokens = account(client)
    rotated = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert rotated.status_code == 200
    assert rotated.json()["refresh_token"] != tokens["refresh_token"]
    assert rotated.headers["cache-control"] == "no-store"
    assert client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401
    assert client.get("/users/me", headers=headers(rotated.json())).status_code == 200


def test_expired_refresh_token_rejected(client, db):
    _, tokens = account(client)
    session = db.get(RefreshSession, refresh_token_hash(tokens["refresh_token"]))
    session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.commit()
    assert client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401


def test_logout_revokes_access_and_refresh(client):
    _, tokens = account(client)
    assert client.post("/auth/logout", headers=headers(tokens)).status_code == 204
    assert client.get("/users/me", headers=headers(tokens)).status_code == 401
    assert client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401


def test_password_change_revokes_sessions(client):
    _, tokens = account(client)
    assert client.patch("/users/me", json={"password": "AnotherStrongPass!"}, headers=headers(tokens)).status_code == 200
    assert client.get("/users/me", headers=headers(tokens)).status_code == 401
    assert client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401
    assert client.post("/auth/token", data={"username": "member@test.com", "password": PASSWORD}).status_code == 401


@pytest.mark.parametrize("password", ["short", "é" * 37, None])
def test_password_policy_applies_to_updates(client, password):
    _, tokens = account(client)
    assert client.patch("/users/me", json={"password": password}, headers=headers(tokens)).status_code == 422


def test_disabled_account_rejected_everywhere(client, admin_headers):
    user, tokens = account(client)
    assert client.patch(f"/users/{user['id']}", json={"is_active": False}, headers=admin_headers).status_code == 200
    assert client.get("/users/me", headers=headers(tokens)).status_code == 401
    assert client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401
    assert client.post("/auth/token", data={"username": user["email"], "password": PASSWORD}).status_code == 401


def test_client_ownership_and_admin_access(client, admin_headers):
    owner, owner_tokens = account(client, "owner@test.com")
    _, other_tokens = account(client, "other@test.com")
    result = client.post("/clients/", json={"full_name": "Private client", "owner_user_id": owner["id"]}, headers=admin_headers)
    assert result.status_code == 201
    client_id = result.json()["id"]
    assert client.get(f"/clients/{client_id}", headers=headers(owner_tokens)).status_code == 200
    assert client.get(f"/clients/{client_id}", headers=headers(other_tokens)).status_code == 404
    assert client.get("/clients/", headers=headers(other_tokens)).json() == []
    assert client.patch(f"/clients/{client_id}", json={"notes": "denied"}, headers=headers(other_tokens)).status_code == 404
    assert client.delete(f"/clients/{client_id}", headers=headers(other_tokens)).status_code == 404
    assert client.patch(f"/clients/{client_id}", json={"owner_user_id": None}, headers=headers(owner_tokens)).status_code == 403
    assert client.post("/clients/", json={"full_name": "No self provisioning"}, headers=headers(other_tokens)).status_code == 403
    assert client.get(f"/clients/{client_id}", headers=admin_headers).status_code == 200


def test_unassigned_legacy_clients_are_admin_only(client, admin_headers):
    _, tokens = account(client)
    record = client.post("/clients/", json={"full_name": "Legacy client"}, headers=admin_headers).json()
    assert client.get(f"/clients/{record['id']}", headers=headers(tokens)).status_code == 404
    assert client.get(f"/clients/{record['id']}", headers=admin_headers).status_code == 200


def test_cors_accepts_authorization_and_write_methods(client):
    for method in ("GET", "PATCH", "DELETE"):
        result = client.options("/clients/", headers={"Origin": "https://www.detroitfamilyhomecare.com", "Access-Control-Request-Method": method, "Access-Control-Request-Headers": "authorization,content-type"})
        assert result.status_code == 200
    assert client.options("/clients/", headers={"Origin": "https://untrusted.example", "Access-Control-Request-Method": "GET"}).status_code == 400


def test_rate_limit_enforced():
    limiter = AuthRateLimiter(limit=2)
    request = Request({"type": "http", "client": ("127.0.0.1", 1234)})
    limiter.check(request)
    limiter.check(request)
    with pytest.raises(Exception) as error:
        limiter.check(request)
    assert error.value.status_code == 429


@pytest.mark.parametrize("secret", ["", "short", "REPLACE_WITH_OUTPUT_OF_OPENSSL_RAND_HEX_32"])
def test_production_rejects_bad_secrets(secret):
    env = {**os.environ, "TESTING": "false", "SECRET_KEY": secret}
    result = subprocess.run([sys.executable, "-c", "import dfhc.app.core.config"], env=env, capture_output=True)
    assert result.returncode != 0
