from __future__ import annotations

from typing import Optional


def extract_pdf_text_from_path(file_path: str) -> str:
    """Extract text from a stored PDF file.

    Uses PyPDF2 to read multi-page PDFs and concatenate page text.
    """

    from PyPDF2 import PdfReader  # type: ignore # local import

    reader = PdfReader(file_path)
    parts: list[str] = []

    for page in reader.pages:
        txt: Optional[str] = None
        try:
            txt = page.extract_text()
        except Exception:
            txt = None

        if txt:
            parts.append(txt)

    # Clean up whitespace a bit for readability
    return "\n".join(parts).strip()

