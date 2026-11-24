
import pymupdf
import pytest

from backend.app.ingestion.parser import extract_text_from_pdf


def create_pdf(path, pages):
    """Create a temporary PDF containing the supplied page texts."""
    document = pymupdf.open()

    for text in pages:
        page = document.new_page()
        if text:
            page.insert_text((72, 72), text)

    document.save(path)
    document.close()

    return path


def test_extract_text_from_single_page_pdf(tmp_path):
    pdf_path = create_pdf(
        tmp_path / "single.pdf",
        ["KnowFlow AI engineering document"]
    )

    result = extract_text_from_pdf(pdf_path)

    assert len(result) == 1
    assert result[0]["page_number"] == 1
    assert "KnowFlow AI" in result[0]["text"]


def test_extract_text_from_multiple_pages(tmp_path):
    pdf_path = create_pdf(
        tmp_path / "multiple.pdf",
        [
            "Transformer architecture",
            "Attention mechanism",
            "Positional encoding",
        ]
    )

    result = extract_text_from_pdf(pdf_path)

    assert len(result) == 3
    assert [page["page_number"] for page in result] == [1, 2, 3]

    assert "Transformer architecture" in result[0]["text"]
    assert "Attention mechanism" in result[1]["text"]
    assert "Positional encoding" in result[2]["text"]


def test_empty_pdf_returns_empty_list(tmp_path):
    pdf_path = create_pdf(
        tmp_path / "empty.pdf",
        [""]
    )

    result = extract_text_from_pdf(pdf_path)

    assert result == []
def test_blank_pages_are_skipped(tmp_path):
    pdf_path = create_pdf(
        tmp_path / "blank_pages.pdf",
        [
            "First page content",
            "",
            "Third page content",
        ]
    )

    result = extract_text_from_pdf(pdf_path)

    assert len(result) == 2
    assert result[0]["page_number"] == 1
    assert result[1]["page_number"] == 3


def test_missing_pdf_raises_error(tmp_path):
    pdf_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError, match="PDF not found"):
        extract_text_from_pdf(pdf_path)


def test_non_pdf_file_raises_error(tmp_path):
    file_path = tmp_path / "document.txt"
    file_path.write_text("This is not a PDF.")

    with pytest.raises(ValueError, match="Expected a PDF file"):
        extract_text_from_pdf(file_path)


def test_invalid_pdf_raises_error(tmp_path):
    pdf_path = tmp_path / "corrupt.pdf"
    pdf_path.write_bytes(b"This is not a valid PDF")

    with pytest.raises(Exception):
        extract_text_from_pdf(pdf_path)
