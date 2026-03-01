import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dfhc.app.core.database import Base, get_db
from dfhc.main import app

TEST_DB_URL = 'sqlite:///./test_dfhc.db'
engine = create_engine(TEST_DB_URL, connect_args={'check_same_thread': False})
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
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_create_user():
    r = client.post('/users/', json={'email': 'alice@dfhc.test', 'password': 'secret123', 'full_name': 'Alice Test'})
    assert r.status_code == 201
    data = r.json()
    assert data['email'] == 'alice@dfhc.test'
    assert 'id' in data

def test_create_duplicate_user():
    client.post('/users/', json={'email': 'bob@dfhc.test', 'password': 'secret', 'full_name': 'Bob'})
    r = client.post('/users/', json={'email': 'bob@dfhc.test', 'password': 'secret', 'full_name': 'Bob'})
    assert r.status_code == 400

def test_list_users():
    r = client.get('/users/')
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_get_user_not_found():
    r = client.get('/users/99999')
    assert r.status_code == 404
