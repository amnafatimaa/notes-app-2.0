import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from starlette.testclient import TestClient
from main import app  
from database import Base, get_db, SessionLocal, NoteDB

app.dependency_overrides[get_db] = get_db

@pytest.fixture(scope="function")
def setup_teardown_db():
    Base.metadata.create_all(bind=SessionLocal().bind)
    yield
    db = SessionLocal()
    db.query(NoteDB).delete()
    db.commit()
    db.close()

@pytest.fixture
def client(setup_teardown_db):
    with TestClient(app) as client:
        yield client

def test_get_notes(client, setup_teardown_db):
    db = SessionLocal()
    test_note = NoteDB(id="test-id-1", title="Test Title", content="Test Content")
    db.add(test_note)
    db.commit()
    db.close()

    response = client.get("/notes")  
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "test-id-1"
    assert data[0]["title"] == "Test Title"
    assert data[0]["content"] == "Test Content"

def test_create_note(client, setup_teardown_db):
    note_data = {"title": "New Note", "content": "New Content"}
    response = client.post("/notes", json=note_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Note"
    assert data["content"] == "New Content"
    assert len(data["id"]) > 0

def test_get_note(client, setup_teardown_db):
    db = SessionLocal()
    test_note = NoteDB(id="test-id-2", title="Get Test", content="Get Content")
    db.add(test_note)
    db.commit()
    db.close()

    response = client.get("/notes/test-id-2")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-id-2"
    assert data["title"] == "Get Test"
    assert data["content"] == "Get Content"

def test_update_note(client, setup_teardown_db):
    db = SessionLocal()
    test_note = NoteDB(id="test-id-3", title="Old Title", content="Old Content")
    db.add(test_note)
    db.commit()
    db.close()

    update_data = {"title": "Updated Title", "content": "Updated Content"}
    response = client.put("/notes/test-id-3", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-id-3"
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"

def test_delete_note(client, setup_teardown_db):
    db = SessionLocal()
    test_note = NoteDB(id="test-id-4", title="Delete Test", content="Delete Content")
    db.add(test_note)
    db.commit()
    db.close()

    response = client.delete("/notes/test-id-4")
    assert response.status_code == 200
    assert response.json() == {"message": "Note deleted"}

    response = client.get("/notes/test-id-4")
    assert response.status_code == 404
