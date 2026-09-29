"""Shared test setup: one in-memory SQLite DB for the whole test session.

Previously each test module installed its own get_db override at import time,
so whichever module was imported last silently won. Keeping the setup here
makes every test use the same, predictable database.
"""

import os

os.environ["TESTING"] = "1"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-at-least-32-chars"
os.environ["DATABASE_URL"] = "sqlite://"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import dfhc.app.models  # noqa: F401,E402
from dfhc.app.core.database import Base, get_db  # noqa: E402
from dfhc.app.repositories import users as user_repo  # noqa: E402
from dfhc.app.schemas import UserCreate  # noqa: E402
from dfhc.main import app  # noqa: E402

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

ADMIN_EMAIL = "admin@dfhc.test"
ADMIN_PASSWORD = "AdminPass12345"


def _login(client: TestClient, email: str, password: str) -> dict:
    r = client.post("/auth/token", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def admin_headers(client) -> dict:
    db = TestingSessionLocal()
    try:
        if not user_repo.get_user_by_email(db, ADMIN_EMAIL):
            user_repo.create_user(
                db, UserCreate(email=ADMIN_EMAIL, password=ADMIN_PASSWORD), is_superuser=True
            )
    finally:
        db.close()
    return _login(client, ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture
def make_staff(client, admin_headers):
    """Create (or reuse) a non-admin staff user and return its auth headers."""

    def _make(email: str, password: str = "StaffPass12345") -> dict:
        r = client.post("/users/", json={"email": email, "password": password}, headers=admin_headers)
        assert r.status_code in (201, 400), r.text
        return _login(client, email, password)

    return _make
