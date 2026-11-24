
import pytest

from backend.app.ingestion import pipeline


def test_ingest_pdf_success(monkeypatch, tmp_path):
    pdf_path = tmp_path / "attention.pdf"
    
    pages = [
        {"page_number": 1, "text": "Page one content"},
        {"page_number": 2, "text": "Page two content"},
    ]

    monkeypatch.setattr(
        pipeline,
        "extract_text_from_pdf",
        lambda path: pages
    )

    def mock_chunk_text(text, chunk_size, overlap):
        return [f"Chunk from {text}"]

    monkeypatch.setattr(
        pipeline,
        "chunk_text",
        mock_chunk_text
    )

    result = pipeline.ingest_pdf(pdf_path)

    assert len(result) == 2

    assert result[0]["text"] == "Chunk from Page one content"
    assert result[0]["metadata"] == {
        "source": "attention.pdf",
        "page_number": 1,
        "chunk_index": 0,
    }

    assert result[1]["metadata"] == {
        "source": "attention.pdf",
        "page_number": 2,
        "chunk_index": 1,
    }


def test_ingest_pdf_multiple_chunks_per_page(monkeypatch, tmp_path):
    pdf_path = tmp_path / "attention.pdf"

    pages = [
        {"page_number": 1, "text": "Page one"},
        {"page_number": 2, "text": "Page two"},
    ]

    monkeypatch.setattr(
        pipeline,
        "extract_text_from_pdf",
        lambda path: pages
    )

    monkeypatch.setattr(
        pipeline,
        "chunk_text",
        lambda text, chunk_size, overlap: [
            f"{text} chunk A",
            f"{text} chunk B",
        ]
    )

    result = pipeline.ingest_pdf(pdf_path)

    assert len(result) == 4

    assert [item["metadata"]["chunk_index"] for item in result] == [
        0, 1, 2, 3
    ]

    assert [item["metadata"]["page_number"] for item in result] == [
        1, 1, 2, 2
    ]


def test_ingest_pdf_empty_document(monkeypatch, tmp_path):
    monkeypatch.setattr(
        pipeline,
        "extract_text_from_pdf",
        lambda path: []
    )

    result = pipeline.ingest_pdf(tmp_path / "empty.pdf")

    assert result == []


def test_ingest_pdf_passes_chunk_parameters(monkeypatch, tmp_path):
    captured = {}

    monkeypatch.setattr(
        pipeline,
        "extract_text_from_pdf",
        lambda path: [
            {"page_number": 1, "text": "Sample content"}
        ]
    )

    def mock_chunk_text(text, chunk_size, overlap):
        captured["chunk_size"] = chunk_size
        captured["overlap"] = overlap
        return ["Sample chunk"]

    monkeypatch.setattr(
        pipeline,
        "chunk_text",
        mock_chunk_text
    )

    pipeline.ingest_pdf(
        tmp_path / "sample.pdf",
        chunk_size=300,
        overlap=60,
    )

    assert captured["chunk_size"] == 300
    assert captured["overlap"] == 60


def test_ingest_pdf_propagates_extraction_error(monkeypatch, tmp_path):
    def mock_extract(path):
        raise ValueError("Unable to extract PDF")

    monkeypatch.setattr(
        pipeline,
        "extract_text_from_pdf",
        mock_extract
    )

    with pytest.raises(ValueError, match="Unable to extract PDF"):
        pipeline.ingest_pdf(tmp_path / "corrupt.pdf")
