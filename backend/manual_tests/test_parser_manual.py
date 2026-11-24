
from pathlib import Path

from backend.app.ingestion.parser import extract_text_from_pdf


pdf_path = Path(input("Enter the full path to a PDF: ").strip().strip('"'))

pages = extract_text_from_pdf(pdf_path)

print(f"\nPages containing text: {len(pages)}")

for page in pages[:2]:
    print(f"\n--- Page {page['page_number']} ---")
    print(page["text"][:1000])
