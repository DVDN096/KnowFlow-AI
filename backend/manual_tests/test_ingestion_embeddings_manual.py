from pathlib import Path

from backend.app.ingestion.service import IngestionService


pdf_path = Path(
    input("Enter the full path to your PDF: ").strip().strip('"')
)

service = IngestionService()
chunks = service.process_pdf(pdf_path)

print(f"\nTotal chunks: {len(chunks)}")

if chunks:
    first_chunk = chunks[0]

    print(f"Source: {first_chunk['metadata']['source']}")
    print(f"Page: {first_chunk['metadata']['page_number']}")
    print(f"Chunk index: {first_chunk['metadata']['chunk_index']}")
    print(f"Embedding dimensions: {len(first_chunk['embedding'])}")
    print(f"Text preview: {first_chunk['text'][:200]}")