from backend.app.ingestion.embedder import Embedder

embedder = Embedder()

texts = [
    "PostgreSQL stores structured data in tables.",
    "Vector search finds semantically similar text.",
    "The server room has cooling equipment.",
]

embeddings = embedder.embed_texts(texts)

print(f"Number of embeddings: {len(embeddings)}")
print(f"Embedding dimensions: {len(embeddings[0])}")
print(f"First five values: {embeddings[0][:5]}")

query_vector = embedder.embed_query(
    "How can I search for similar documents?"
)

print(f"Query embedding dimensions: {len(query_vector)}")