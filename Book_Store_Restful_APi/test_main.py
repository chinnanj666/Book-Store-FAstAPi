from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()

    # Print actual response for debugging (optional)
    print("Root endpoint response:", data)

    # Flexible check: only assert the keys that matter
    assert data.get("status") == "running"
    assert data.get("version") == "1.0"
    assert data.get("docs") == "/docs"

def test_add_book():
    book_data = {
        "id": 1,
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "price": 12.99
    }
    response = client.post("/books", json=book_data)
    assert response.status_code == 201
    assert response.json()["title"] == "The Hobbit"

def test_get_books():
    response = client.get("/books")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_book_not_found():
    response = client.get("/books/999")
    assert response.status_code == 404
