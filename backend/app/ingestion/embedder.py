
import os
import math

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
GEMINI_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 384

# Allows existing tests to mock SentenceTransformer.
# The actual library is imported only when required.
SentenceTransformer = None


class Embedder:
    def __init__(self, model_name: str = MODEL_NAME):
        self.provider = os.getenv(
            "EMBEDDING_PROVIDER", "sentence_transformers"
        ).lower()

        if self.provider == "sentence_transformers":
            global SentenceTransformer

            if SentenceTransformer is None:
                from sentence_transformers import SentenceTransformer as ST
                SentenceTransformer = ST

            self.model = SentenceTransformer(model_name)

        elif self.provider == "gemini":
            from google import genai
            from google.genai import types

            api_key = os.getenv("GEMINI_API_KEY")

            if not api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY is not configured."
                )

            self.client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(
                    api_version="v1beta"
                ),
            )

        else:
            raise ValueError(
                f"Unsupported EMBEDDING_PROVIDER: {self.provider}"
            )

    def _normalize(self, vector: list[float]) -> list[float]:
        norm = math.sqrt(sum(value * value for value in vector))

        if norm == 0:
            raise RuntimeError("Received a zero-length embedding.")

        return [value / norm for value in vector]

    def _embed_with_gemini(
        self,
        texts: list[str],
        task_type: str,
    ) -> list[list[float]]:
        if not texts:
            return []

        from google.genai import types

        response = self.client.models.embed_content(
            model=GEMINI_MODEL,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=EMBEDDING_DIMENSIONS,
            ),
        )

        if not response.embeddings:
            raise RuntimeError("Gemini returned no embeddings.")

        if len(response.embeddings) != len(texts):
            raise RuntimeError(
                "Gemini returned an unexpected number of embeddings."
            )

        return [
            self._normalize(embedding.values)
            for embedding in response.embeddings
        ]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        if self.provider == "gemini":
            return self._embed_with_gemini(
                texts, "RETRIEVAL_DOCUMENT"
            )

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        if self.provider == "gemini":
            return self._embed_with_gemini(
                [query], "RETRIEVAL_QUERY"
            )[0]

        return self.embed_texts([query])[0]
