from backend.app.ingestion.chunker import chunk_text

sample_text = " ".join(f"word{i}" for i in range(1200))

chunks = chunk_text(sample_text)

print(f"Total chunks: {len(chunks)}")

for i, chunk in enumerate(chunks, start=1):
    print(f"Chunk {i}: {len(chunk.split())} words")