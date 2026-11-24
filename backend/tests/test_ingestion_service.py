
from unittest.mock import MagicMock

import pytest

from backend.app.ingestion import service


@pytest.fixture
def ingestion_service(monkeypatch):
    mock_embedder = MagicMock()

    monkeypatch.setattr(
        service,
        "Embedder",
        lambda: mock_embedder
    )

    instance = service.IngestionService()

    return instance, mock_embedder


def test_process_pdf_success(ingestion_service, monkeypatch):
    instance, mock_embedder = ingestion_service

    chunks = [
        {"text": "First chunk", "page_number": 1, "chunk_index": 0},
        {"text": "Second chunk", "page_number": 2, "chunk_index": 1},
    ]

    embeddings = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    monkeypatch.setattr(
        service,
        "ingest_pdf",
        lambda file_path: chunks
    )

    mock_embedder.embed_texts.return_value = embeddings

    result = instance.process_pdf("sample.pdf")

    assert len(result) == 2
    assert result[0]["embedding"] == embeddings[0]
    assert result[1]["embedding"] == embeddings[1]

    mock_embedder.embed_texts.assert_called_once_with(
        ["First chunk", "Second chunk"]
    )


def test_process_pdf_empty_chunks(ingestion_service, monkeypatch):
    instance, mock_embedder = ingestion_service

    monkeypatch.setattr(
        service,
        "ingest_pdf",
        lambda file_path: []
    )

    result = instance.process_pdf("empty.pdf")

    assert result == []
    mock_embedder.embed_texts.assert_not_called()


def test_process_pdf_preserves_metadata(ingestion_service, monkeypatch):
    instance, mock_embedder = ingestion_service

    chunks = [
        {
            "text": "Transformer architecture",
            "page_number": 5,
            "chunk_index": 3,
            "source": "attention.pdf",
        }
    ]

    mock_embedder.embed_texts.return_value = [[0.1, 0.2, 0.3]]

    monkeypatch.setattr(
        service,
        "ingest_pdf",
        lambda file_path: chunks
    )

    result = instance.process_pdf("attention.pdf")

    assert result[0]["page_number"] == 5
    assert result[0]["chunk_index"] == 3
    assert result[0]["source"] == "attention.pdf"
    assert "embedding" in result[0]


def test_process_pdf_propagates_extraction_error(
    ingestion_service,
    monkeypatch
):
    instance, mock_embedder = ingestion_service

    def mock_ingest_pdf(file_path):
        raise ValueError("PDF extraction failed")

    monkeypatch.setattr(
        service,
        "ingest_pdf",
        mock_ingest_pdf
    )

    with pytest.raises(ValueError, match="PDF extraction failed"):
        instance.process_pdf("corrupt.pdf")

    mock_embedder.embed_texts.assert_not_called()
