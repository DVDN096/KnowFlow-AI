from pathlib import Path

from backend.app.db.connection import get_connection
from backend.app.db.repository import save_document
from backend.app.ingestion.service import IngestionService


# Check database connectivity first.
with get_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        print("pgvector installed:", cursor.fetchone() is not None)

        cursor.execute("SELECT COUNT(*) FROM documents")
        print("Existing documents:", cursor.fetchone()[0])


pdf_path = Path(
    input("\nEnter the full path to your PDF: ").strip().strip('"')
)

chunks = IngestionService().process_pdf(pdf_path)

if not chunks:
    raise RuntimeError("No text chunks were extracted from this PDF.")

document_id = save_document(pdf_path, chunks)

print(f"\nDocument saved successfully. ID: {document_id}")
print(f"Chunks saved: {len(chunks)}")