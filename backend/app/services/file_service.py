import os
import uuid
from io import BytesIO
from typing import Any, Dict

from fastapi import UploadFile # type: ignore

from app.core.config import settings
from app.services.pdf_errors import (
    EmptyPDFError,
    EncryptedPDFError,
    PDFPageCountExceededError,
    PDFUploadTooLargeError,
)


def find_stored_pdf(upload_dir: str, document_id: str) -> str:
    """Resolve a document ID to a PDF present in the server-owned upload directory."""
    try:
        canonical_id = str(uuid.UUID(document_id))
    except (ValueError, AttributeError) as exc:
        raise FileNotFoundError("Stored PDF not found") from exc

    prefix = f"{canonical_id}__"
    try:
        entries = os.scandir(upload_dir)
    except FileNotFoundError as exc:
        raise FileNotFoundError("Stored PDF not found") from exc

    with entries:
        for entry in entries:
            if (
                entry.name.startswith(prefix)
                and entry.name.lower().endswith(".pdf")
                and entry.is_file(follow_symlinks=False)
            ):
                return entry.path

    raise FileNotFoundError("Stored PDF not found")


def remove_stored_pdf(upload_dir: str, document_id: str) -> None:
    try:
        os.remove(find_stored_pdf(upload_dir, document_id))
    except FileNotFoundError:
        pass


def store_pdf(upload_dir: str, upload_file: UploadFile) -> Dict[str, Any]:
    """Validate and store an uploaded PDF.

    - Validates content-type/extension and basic PDF signature.
    - Saves to disk under `upload_dir`.
    """

    original_name = upload_file.filename or ""
    if not original_name.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported")

    doc_id = str(uuid.uuid4())
    safe_name = os.path.splitext(os.path.basename(original_name))[0].strip().replace(" ", "_")
    filename = f"{doc_id}__{safe_name}.pdf"
    content = upload_file.file.read(settings.max_pdf_upload_bytes + 1)
    if len(content) > settings.max_pdf_upload_bytes:
        raise PDFUploadTooLargeError("PDF exceeds the configured upload limit")

    # Basic signature check (PDFs start with %PDF-)
    if not content.startswith(b"%PDF-"):
        raise ValueError("Uploaded file does not appear to be a valid PDF")

    try:
        from PyPDF2 import PdfReader  # type: ignore

        reader = PdfReader(BytesIO(content), strict=False)
        if reader.is_encrypted:
            raise EncryptedPDFError("Encrypted PDFs are not supported")
        page_count = len(reader.pages)
        if page_count == 0:
            raise EmptyPDFError("PDF contains no pages")
        if page_count > settings.max_pdf_pages:
            raise PDFPageCountExceededError("PDF exceeds the configured page limit")
    except (
        EncryptedPDFError,
        EmptyPDFError,
        PDFPageCountExceededError,
        PDFUploadTooLargeError,
    ):
        raise
    except Exception as exc:  # noqa: BLE001
        raise ValueError("Uploaded file is not a readable PDF") from exc

    os.makedirs(upload_dir, exist_ok=True)
    dest_path = os.path.join(upload_dir, filename)
    with open(dest_path, "xb") as output_file:
        output_file.write(content)

    return {
        "id": doc_id,
        "name": original_name,
        "size": os.path.getsize(dest_path),
        "uploadedAt": int(os.path.getmtime(dest_path) * 1000),
    }
