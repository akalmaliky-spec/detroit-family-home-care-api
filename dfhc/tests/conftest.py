import os
import pytest

os.environ["TESTING"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-at-least-32-chars"
os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402
from dfhc.app.core.database import Base, get_db  # noqa: E402
from dfhc.app.core.rate_limit import auth_rate_limiter  # noqa: E402
from dfhc.app.models import User  # noqa: E402
from dfhc.main import app  # noqa: E402


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine, autoflush=False)() as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(db):
    def override():
        yield db
    app.dependency_overrides[get_db] = override
    auth_rate_limiter.attempts.clear()
    with TestClient(app) as http:
        yield http
    app.dependency_overrides.clear()
    auth_rate_limiter.attempts.clear()


@pytest.fixture
def admin_headers(client, db):
    client.post("/users/", json={"email": "admin@test.com", "password": "StrongPass123!"})
    user = db.query(User).filter(User.email == "admin@test.com").one()
    user.is_superuser = True
    db.commit()
    result = client.post("/auth/token", data={"username": user.email, "password": "StrongPass123!"})
    assert result.status_code == 200
    return {"Authorization": "Bearer " + result.json()["access_token"]}
