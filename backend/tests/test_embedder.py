
from unittest.mock import MagicMock

import pytest

from backend.app.ingestion import embedder


@pytest.fixture
def mock_embedder(monkeypatch):
    mock_model = MagicMock()

    monkeypatch.setattr(
        embedder,
        "SentenceTransformer",
        lambda model_name: mock_model
    )

    instance = embedder.Embedder()

    return instance, mock_model


def test_model_initialization(mock_embedder):
    instance, mock_model = mock_embedder

    assert instance.model is mock_model


def test_embed_texts_success(mock_embedder):
    instance, mock_model = mock_embedder

    expected_embeddings = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    mock_model.encode.return_value.tolist.return_value = (
        expected_embeddings
    )

    result = instance.embed_texts([
        "Transformer architecture",
        "Attention mechanism",
    ])

    assert result == expected_embeddings

    mock_model.encode.assert_called_once_with(
        [
            "Transformer architecture",
            "Attention mechanism",
        ],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    )


def test_embed_texts_empty_input(mock_embedder):
    instance, mock_model = mock_embedder

    result = instance.embed_texts([])

    assert result == []
    mock_model.encode.assert_not_called()


def test_embed_query_success(mock_embedder):
    instance, mock_model = mock_embedder

    expected_embedding = [0.1, 0.2, 0.3]

    mock_model.encode.return_value.tolist.return_value = [
        expected_embedding
    ]

    result = instance.embed_query("What is attention?")

    assert result == expected_embedding

    mock_model.encode.assert_called_once()


def test_embedding_model_error_propagates(mock_embedder):
    instance, mock_model = mock_embedder

    mock_model.encode.side_effect = RuntimeError(
        "Embedding generation failed"
    )

    with pytest.raises(
        RuntimeError,
        match="Embedding generation failed"
    ):
        instance.embed_texts(["Sample text"])
