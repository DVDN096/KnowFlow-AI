from pathlib import Path

from backend.app.ingestion.pipeline import ingest_pdf
from backend.app.ingestion.embedder import Embedder


class IngestionService:
    def __init__(self):
        # Load the model once, not for every document.
        self.embedder = Embedder()

    def process_pdf(self, file_path: str | Path) -> list[dict]:
        # Step 1: Extract text and create chunks with metadata.
        chunks = ingest_pdf(file_path)

        if not chunks:
            return []

        # Step 2: Generate one embedding per chunk.
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedder.embed_texts(texts)

        # Step 3: Attach each vector to its corresponding chunk.
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding

        return chunks