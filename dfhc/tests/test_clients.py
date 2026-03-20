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

TEST_DB = "sqlite:///./test_dfhc_clients.db"
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


def test_create_client():
    r = client.post("/clients/", json=CLIENT_PAYLOAD)
    assert r.status_code == 201
    data = r.json()
    assert data["full_name"] == "Mary Johnson"
    assert data["id"] is not None


def test_list_clients():
    r = client.get("/clients/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_client_not_found():
    r = client.get("/clients/99999")
    assert r.status_code == 404


def test_get_client_by_id():
    create_r = client.post("/clients/", json={**CLIENT_PAYLOAD, "full_name": "Test Client"})
    assert create_r.status_code == 201
    client_id = create_r.json()["id"]
    r = client.get(f"/clients/{client_id}")
    assert r.status_code == 200
    assert r.json()["full_name"] == "Test Client"


def test_update_client():
    create_r = client.post("/clients/", json={**CLIENT_PAYLOAD, "full_name": "Update Me"})
    client_id = create_r.json()["id"]
    r = client.patch(f"/clients/{client_id}", json={"full_name": "Updated Name"})
    assert r.status_code == 200
    assert r.json()["full_name"] == "Updated Name"


def test_delete_client():
    create_r = client.post("/clients/", json={**CLIENT_PAYLOAD, "full_name": "Delete Me"})
    client_id = create_r.json()["id"]
    r = client.delete(f"/clients/{client_id}")
    assert r.status_code == 204
    r2 = client.get(f"/clients/{client_id}")
    assert r2.status_code == 404
