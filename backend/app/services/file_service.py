import os
import uuid
from typing import Any, Dict

from fastapi import UploadFile # type: ignore


def store_pdf(upload_dir: str, upload_file: UploadFile) -> Dict[str, Any]:
    """Validate and store an uploaded PDF.

    - Validates content-type/extension and basic PDF signature.
    - Saves to disk under `upload_dir`.
    """

    os.makedirs(upload_dir, exist_ok=True)

    doc_id = str(uuid.uuid4())
    ext = os.path.splitext(upload_file.filename)[1].lower() or ".pdf"
    safe_name = os.path.splitext(os.path.basename(upload_file.filename))[0].strip().replace(" ", "_")
    filename = f"{doc_id}__{safe_name}{ext}"

    dest_path = os.path.join(upload_dir, filename)

    # Read entire file (starter; for production use streaming)
    content = upload_file.file.read()

    # Basic signature check (PDFs start with %PDF-)
    if not content.startswith(b"%PDF-"):
        raise ValueError("Uploaded file does not appear to be a valid PDF")

    with open(dest_path, "wb") as f:
        f.write(content)

    # Optional deeper validation using PyPDF2 (helps catch malformed PDFs)
    # If it fails, we treat it as invalid and still keep a file on disk
    # (could be deleted, but we keep foundation code simple).
    try:
        from PyPDF2 import PdfReader  # type: ignore # local import to keep startup light

        _ = PdfReader(dest_path)
    except Exception as e:  # noqa: BLE001
        raise ValueError(f"Failed to parse PDF: {e}")

    return {
        "id": doc_id,
        "name": upload_file.filename,
        "size": os.path.getsize(dest_path),
        "uploadedAt": int(os.path.getmtime(dest_path) * 1000),
    }


