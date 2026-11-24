
from pathlib import Path

import pymupdf


def extract_text_from_pdf(file_path: str | Path) -> list[dict]:
    """
    Extract text page by page from a PDF.

    Returns a list of dictionaries containing each page's
    page number and extracted text.
    """
    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Expected a PDF file.")

    pages = []

    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "page_number": page_number,
                    "text": text,
                })

    return pages
