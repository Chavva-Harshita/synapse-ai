from __future__ import annotations

from typing import Optional

from app.core.config import settings
from app.services.pdf_errors import (
    PDFExtractionError,
    PDFPageCountExceededError,
    PDFTextLimitExceededError,
)


def extract_pdf_text_from_path(file_path: str) -> str:
    """Extract text from a stored PDF file.

    Uses PyPDF2 to read multi-page PDFs and concatenate page text.
    """

    from PyPDF2 import PdfReader  # type: ignore # local import

    try:
        reader = PdfReader(file_path, strict=False)
        if reader.is_encrypted:
            raise PDFExtractionError("Encrypted PDFs are not supported")
        page_count = len(reader.pages)
    except PDFExtractionError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise PDFExtractionError("The PDF could not be opened for text extraction") from exc

    if page_count > settings.max_pdf_pages:
        raise PDFPageCountExceededError("PDF exceeds the configured page limit")

    parts: list[str] = []
    extracted_characters = 0

    for page_number, page in enumerate(reader.pages, start=1):
        try:
            txt: Optional[str] = page.extract_text()
        except Exception as exc:  # noqa: BLE001
            raise PDFExtractionError(
                f"Could not extract text from PDF page {page_number}"
            ) from exc

        if txt:
            extracted_characters += len(txt)
            if extracted_characters > settings.max_pdf_extracted_chars:
                raise PDFTextLimitExceededError(
                    "PDF extracted text exceeds the configured character limit"
                )
            parts.append(txt)

    # Clean up whitespace a bit for readability
    return "\n".join(parts).strip()
