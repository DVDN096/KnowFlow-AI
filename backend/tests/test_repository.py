
from unittest.mock import MagicMock, patch

import pytest

from backend.app.db import repository


@pytest.fixture
def mock_database():
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    with patch(
        "backend.app.db.repository.get_connection",
        return_value=connection
    ):
        yield cursor


def test_calculate_sha256(tmp_path):
    file_path = tmp_path / "sample.pdf"
    file_path.write_bytes(b"KnowFlow AI test document")

    result = repository.calculate_sha256(file_path)

    assert len(result) == 64
    assert result == repository.calculate_sha256(file_path)


@patch("backend.app.db.repository.Vector")
@patch("backend.app.db.repository.Jsonb")
def test_save_document_success(mock_jsonb, mock_vector, mock_database, tmp_path):
    file_path = tmp_path / "sample.pdf"
    file_path.write_bytes(b"%PDF-1.4 sample content")

    mock_database.fetchone.return_value = (42,)

    chunks = [
        {
            "text": "Transformer architecture",
            "metadata": {
                "source": "sample.pdf",
                "page_number": 1,
                "chunk_index": 0,
            },
            "embedding": [0.1, 0.2, 0.3],
        }
    ]

    result = repository.save_document(file_path, chunks)

    assert result == 42
    mock_vector.assert_called_once_with([0.1, 0.2, 0.3])
    mock_jsonb.assert_called_once_with(chunks[0]["metadata"])

    assert mock_database.execute.call_count == 3


def test_save_duplicate_document(mock_database, tmp_path):
    file_path = tmp_path / "duplicate.pdf"
    file_path.write_bytes(b"%PDF-1.4 duplicate content")

    mock_database.fetchone.side_effect = [
        None,
        (15,),
    ]

    with pytest.raises(repository.DuplicateDocumentError) as exc:
        repository.save_document(file_path, [])

    assert exc.value.document_id == 15
    assert mock_database.execute.call_count == 2


def test_list_documents(mock_database):
    mock_database.fetchall.return_value = [
        (1, "attention.pdf", ".pdf", "completed", None, 20),
        (2, "object_detection.pdf", ".pdf", "completed", None, 30),
    ]

    result = repository.list_documents()

    assert len(result) == 2
    assert result[0]["filename"] == "attention.pdf"
    assert result[1]["chunk_count"] == 30


def test_get_document_success(mock_database):
    mock_database.fetchone.return_value = (
        1, "attention.pdf", ".pdf", "completed", None, 20
    )

    result = repository.get_document(1)

    assert result["id"] == 1
    assert result["filename"] == "attention.pdf"
    assert result["chunk_count"] == 20


def test_get_document_not_found(mock_database):
    mock_database.fetchone.return_value = None

    result = repository.get_document(999)

    assert result is None


def test_delete_document_success(mock_database):
    mock_database.fetchone.return_value = (1,)

    assert repository.delete_document(1) is True


def test_delete_document_not_found(mock_database):
    mock_database.fetchone.return_value = None

    assert repository.delete_document(999) is False
