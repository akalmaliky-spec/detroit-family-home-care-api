import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("TESTING", "1")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")

from dfhc.app.core.database import Base, get_db  # noqa: E402
from dfhc.main import app  # noqa: E402
import dfhc.app.models  # noqa: F401,E402

TEST_DB = "sqlite:///./test_dfhc.db"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_create_user():
    r = client.post("/users/", json={"email": "alice@test.com", "password": "AlicePass1!"})
    assert r.status_code == 201
    assert r.json()["email"] == "alice@test.com"

def test_create_user_password_too_short():
    r = client.post("/users/", json={"email": "short@test.com", "password": "short"})
    assert r.status_code == 422

def test_duplicate_user():
    client.post("/users/", json={"email": "dup@test.com", "password": "DupPass1234!"})
    r = client.post("/users/", json={"email": "dup@test.com", "password": "DupPass1234!"})
    assert r.status_code == 400

def test_list_users():
    r = client.get("/users/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_user_not_found():
    r = client.get("/users/99999")
    assert r.status_code == 404
