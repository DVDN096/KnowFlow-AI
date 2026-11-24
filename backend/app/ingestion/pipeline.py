from pathlib import Path

from backend.app.ingestion.parser import extract_text_from_pdf
from backend.app.ingestion.chunker import chunk_text


def ingest_pdf(
    file_path: str | Path,
    chunk_size: int = 250,
    overlap: int = 50,
) -> list[dict]:
    """
    Extract text from a PDF and split each page into chunks.

    Each chunk retains its source filename, page number,
    and chunk index.
    """
    pdf_path = Path(file_path)

    # Stage 1: Extract text page by page.
    pages = extract_text_from_pdf(pdf_path)

    results = []
    chunk_index = 0

    # Stage 2: Split each page into chunks.
    for page in pages:
        page_chunks = chunk_text(
            page["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk in page_chunks:
            results.append(
                {
                    "text": chunk,
                    "metadata": {
                        "source": pdf_path.name,
                        "page_number": page["page_number"],
                        "chunk_index": chunk_index,
                    },
                }
            )
            chunk_index += 1

    return results