from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query # type: ignore

from app.core.config import settings
from app.services.embedding_pipeline import embed_and_store_pdf_chunks
from app.services.file_service import find_stored_pdf
from app.services.pdf_errors import PDFExtractionError, PDFPageCountExceededError, PDFTextLimitExceededError
from app.services.pdf_text_extractor import extract_pdf_text_from_path
from app.services.vector_store import VectorStoreUnavailableError

router = APIRouter(tags=["embeddings"])


def _locate_stored_pdf(document_id: str) -> str:
    return find_stored_pdf(settings.upload_dir, document_id)


@router.post("/embed-and-store")
def embed_and_store(
    document_id: UUID,
    chunk_size: int = Query(default=1000, ge=100, le=10000),
    chunk_overlap: int = Query(default=200, ge=0, le=9999),
):
    try:
        canonical_document_id = str(document_id)
        pdf_path = _locate_stored_pdf(canonical_document_id)
        text = extract_pdf_text_from_path(pdf_path)
        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail="The PDF contains no selectable text to index.",
            )
        if chunk_overlap >= chunk_size:
            raise HTTPException(
                status_code=422,
                detail="chunk_overlap must be smaller than chunk_size.",
            )

        # Minimal doc metadata (matches store_pdf structure)
        doc = {
            "id": canonical_document_id,
            "name": f"{canonical_document_id}.pdf",
        }

        result = embed_and_store_pdf_chunks(
            text=text,
            document=doc,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        return {
            "stored": result["stored"],
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")
    except HTTPException:
        raise
    except (PDFPageCountExceededError, PDFTextLimitExceededError, PDFExtractionError):
        raise HTTPException(
            status_code=422,
            detail="The PDF could not be extracted within the supported limits.",
        )
    except VectorStoreUnavailableError:
        raise HTTPException(status_code=503, detail="Document indexing is unavailable.")
    except Exception:  # noqa: BLE001
        logging.getLogger(__name__).exception("Document indexing failed")
        raise HTTPException(status_code=500, detail="Document indexing failed unexpectedly.")
