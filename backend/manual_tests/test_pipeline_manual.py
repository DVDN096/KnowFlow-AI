from pathlib import Path

from backend.app.ingestion.pipeline import ingest_pdf


pdf_path = Path(
    input("Enter the full path to a PDF: ").strip().strip('"')
)

chunks = ingest_pdf(pdf_path)

print(f"\nTotal chunks created: {len(chunks)}")

for chunk in chunks[:3]:
    print("\n" + "=" * 60)
    print(f"Source: {chunk['metadata']['source']}")
    print(f"Page: {chunk['metadata']['page_number']}")
    print(f"Chunk index: {chunk['metadata']['chunk_index']}")
    print(f"Text preview: {chunk['text'][:300]}")
    