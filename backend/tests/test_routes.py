
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from backend.app.main import app
from backend.app.api import routes


@pytest.fixture
def client():
    return TestClient(app)


# -------------------------
# Health and root endpoints
# -------------------------

def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# -------------------------
# Ask endpoint
# -------------------------

def test_ask_success(client, monkeypatch):
    async def mock_answer_question(question, top_k):
        return {
            "answer": "Transformers use positional encodings.",
            "sources": [],
            "timings": {}
        }

    monkeypatch.setattr(
        routes.answer_service,
        "answer_question",
        mock_answer_question
    )

    response = client.post(
        "/api/v1/ask",
        json={"question": "Explain positional encoding"}
    )

    assert response.status_code == 200
    assert "positional encodings" in response.json()["answer"]


def test_ask_empty_question(client):
    response = client.post(
        "/api/v1/ask",
        json={"question": "   "}
    )

    assert response.status_code == 422


def test_ask_invalid_top_k(client):
    response = client.post(
        "/api/v1/ask",
        json={"question": "Explain Transformers", "top_k": 0}
    )

    assert response.status_code == 422


# -------------------------
# Document upload endpoint
# -------------------------

def test_upload_non_pdf(client):
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("document.txt", b"sample text", "text/plain")}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are supported."


def test_upload_invalid_pdf_signature(client):
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("document.pdf", b"not a pdf", "application/pdf")}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The uploaded file is not a valid PDF."


def test_upload_success(client, monkeypatch):
    monkeypatch.setattr(
        routes.ingestion_service,
        "process_pdf",
        lambda path: [{"text": "Sample extracted content"}]
    )

    monkeypatch.setattr(
        routes,
        "save_document",
        lambda *args, **kwargs: 101
    )

    response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "sample.pdf",
                b"%PDF-1.4 sample content",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 200
    assert response.json()["document_id"] == 101
    assert response.json()["chunks_saved"] == 1
    assert response.json()["status"] == "completed"


def test_upload_duplicate_document(client, monkeypatch):
    def mock_save_document(*args, **kwargs):
        raise routes.DuplicateDocumentError(document_id=10)

    monkeypatch.setattr(
        routes.ingestion_service,
        "process_pdf",
        lambda path: [{"text": "Sample content"}]
    )

    monkeypatch.setattr(
        routes,
        "save_document",
        mock_save_document
    )

    response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "duplicate.pdf",
                b"%PDF-1.4 sample content",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 409
    assert response.json()["detail"]["existing_document_id"] == 10


# -------------------------
# Document retrieval
# -------------------------

def test_list_documents(client, monkeypatch):
    monkeypatch.setattr(
        routes,
        "list_documents",
        lambda: [{"id": 1, "filename": "attention.pdf"}]
    )

    response = client.get("/api/v1/documents")

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_get_document_success(client, monkeypatch):
    monkeypatch.setattr(
        routes,
        "get_document",
        lambda document_id: {
            "id": document_id,
            "filename": "attention.pdf"
        }
    )

    response = client.get("/api/v1/documents/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_document_not_found(client, monkeypatch):
    monkeypatch.setattr(
        routes,
        "get_document",
        lambda document_id: None
    )

    response = client.get("/api/v1/documents/999")

    assert response.status_code == 404


# -------------------------
# Document deletion
# -------------------------

def test_delete_document_success(client, monkeypatch):
    monkeypatch.setattr(
        routes,
        "delete_document",
        lambda document_id: True
    )

    response = client.delete("/api/v1/documents/1")

    assert response.status_code == 200
    assert response.json()["document_id"] == 1


def test_delete_document_not_found(client, monkeypatch):
    monkeypatch.setattr(
        routes,
        "delete_document",
        lambda document_id: False
    )

    response = client.delete("/api/v1/documents/999")

    assert response.status_code == 404
