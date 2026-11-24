
import asyncio
from unittest.mock import MagicMock, patch

import pytest

from backend.app.generation.answer import AnswerService


@pytest.fixture
def answer_service():
    with patch("backend.app.generation.answer.HybridSearch"):
        service = AnswerService()
        service.search_engine = MagicMock()
        return service


def test_empty_question_raises_error(answer_service):
    with pytest.raises(ValueError, match="Question cannot be empty"):
        asyncio.run(answer_service.answer_question("   "))


def test_invalid_top_k_raises_error(answer_service):
    with pytest.raises(ValueError, match="top_k must be at least 1"):
        asyncio.run(
            answer_service.answer_question(
                "Explain Transformers",
                top_k=0,
            )
        )


def test_no_retrieval_results(answer_service):
    answer_service.search_engine.search.return_value = []

    result = asyncio.run(
        answer_service.answer_question(
            "Explain an unknown topic"
        )
    )

    assert "couldn't find relevant information" in result["answer"]
    assert result["sources"] == []
    assert result["timings"]["generation_seconds"] == 0


@patch("backend.app.generation.answer.ollama.chat")
def test_successful_answer_generation(mock_chat, answer_service):
    answer_service.search_engine.search.return_value = [
        {
            "source": "attention.pdf",
            "page_number": 3,
            "chunk_index": 2,
            "text": "Transformers use positional encodings.",
        }
    ]

    mock_chat.return_value = {
        "message": {
            "content": (
                "Transformers use positional encodings. "
                "[attention.pdf, page 3]"
            )
        }
    }

    result = asyncio.run(
        answer_service.answer_question(
            "What are positional encodings?"
        )
    )

    assert "positional encodings" in result["answer"]
    assert len(result["sources"]) == 1
    assert result["sources"][0]["source"] == "attention.pdf"
    assert result["sources"][0]["page_number"] == 3
    assert result["timings"]["generation_seconds"] >= 0

    mock_chat.assert_called_once()


@patch("backend.app.generation.answer.ollama.chat")
def test_hallucination_refusal(mock_chat, answer_service):
    answer_service.search_engine.search.return_value = [
        {
            "source": "attention.pdf",
            "page_number": 3,
            "chunk_index": 2,
            "text": "Transformers use positional encodings.",
        }
    ]

    mock_chat.return_value = {
        "message": {
            "content": (
                "The provided documents do not contain "
                "sufficient information to answer this question."
            )
        }
    }

    result = asyncio.run(
        answer_service.answer_question(
            "What was Microsoft's revenue in 2025?"
        )
    )

    assert "do not contain sufficient information" in result["answer"]
    assert "[" not in result["answer"]

    mock_chat.assert_called_once()
