
import pytest

from backend.app.ingestion.chunker import chunk_text


def test_short_text_returns_single_chunk():
    text = "This is a short engineering document."

    result = chunk_text(text)

    assert len(result) == 1
    assert result[0] == text


def test_empty_text_returns_empty_list():
    assert chunk_text("") == []


def test_whitespace_text_returns_empty_list():
    assert chunk_text("   \n\t  ") == []


def test_exact_chunk_size():
    words = [f"word{i}" for i in range(250)]

    result = chunk_text(" ".join(words))

    assert len(result) == 1
    assert len(result[0].split()) == 250


def test_long_text_creates_overlapping_chunks():
    words = [f"word{i}" for i in range(451)]

    result = chunk_text(" ".join(words))

    assert len(result) == 3
    assert len(result[0].split()) == 250
    assert len(result[1].split()) == 250
    assert len(result[2].split()) == 51

    # Verify 50-word overlap.
    assert result[0].split()[-50:] == result[1].split()[:50]
    assert result[1].split()[-50:] == result[2].split()[:50]


def test_custom_chunk_size_and_overlap():
    words = [f"word{i}" for i in range(20)]

    result = chunk_text(
        " ".join(words),
        chunk_size=10,
        overlap=2,
    )

    assert len(result) == 3
    assert len(result[0].split()) == 10
    assert len(result[1].split()) == 10
    assert len(result[2].split()) == 4

    assert result[0].split()[-2:] == result[1].split()[:2]


def test_invalid_chunk_size():
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        chunk_text("sample text", chunk_size=0)


def test_negative_overlap():
    with pytest.raises(ValueError, match="overlap must be non-negative"):
        chunk_text("sample text", chunk_size=10, overlap=-1)


def test_overlap_equal_to_chunk_size():
    with pytest.raises(ValueError, match="overlap must be non-negative"):
        chunk_text("sample text", chunk_size=10, overlap=10)


def test_overlap_greater_than_chunk_size():
    with pytest.raises(ValueError, match="overlap must be non-negative"):
        chunk_text("sample text", chunk_size=10, overlap=11)
