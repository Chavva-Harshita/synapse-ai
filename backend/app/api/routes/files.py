import logging

from fastapi import APIRouter, File, HTTPException, UploadFile # type: ignore

from app.core.config import settings
from app.services.file_service import find_stored_pdf, remove_stored_pdf, store_pdf
from app.services.pdf_errors import (
    EmptyPDFError,
    EncryptedPDFError,
    PDFExtractionError,
    PDFPageCountExceededError,
    PDFTextLimitExceededError,
    PDFUploadTooLargeError,
)
from app.services.pdf_text_extractor import extract_pdf_text_from_path
from app.services.text_chunker import chunk_text

from app.api.routes.upload_models import ExtractTextResponse
from app.api.routes.upload_rag_models import UploadRagResponse


# ---------------------------------------------------
# LOGGER
# ---------------------------------------------------

log = logging.getLogger(__name__)


def _upload_validation_error(exc: ValueError) -> HTTPException:
    if isinstance(exc, PDFUploadTooLargeError):
        return HTTPException(
            status_code=413,
            detail="PDF exceeds the configured upload size limit.",
        )
    if isinstance(exc, PDFPageCountExceededError):
        return HTTPException(
            status_code=413,
            detail="PDF exceeds the supported page limit.",
        )
    if isinstance(exc, EmptyPDFError):
        return HTTPException(status_code=422, detail="The PDF contains no pages.")
    if isinstance(exc, EncryptedPDFError):
        return HTTPException(
            status_code=422,
            detail="Encrypted PDFs are not supported.",
        )
    return HTTPException(
        status_code=400,
        detail="Invalid PDF file. Upload a readable PDF document.",
    )


def _extraction_error(exc: ValueError) -> HTTPException:
    if isinstance(exc, (PDFPageCountExceededError, PDFTextLimitExceededError)):
        return HTTPException(
            status_code=413,
            detail="The PDF exceeds the supported extraction limits.",
        )
    return HTTPException(
        status_code=422,
        detail="The PDF text could not be extracted. Scanned/image-only PDFs are not supported.",
    )


# ---------------------------------------------------
# ROUTER
# ---------------------------------------------------

router = APIRouter()


# ---------------------------------------------------
# SIMPLE PDF UPLOAD
# ---------------------------------------------------

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    """
    Uploads and stores PDF only.
    No RAG processing here.
    """

    log.info(
        "Upload request received: filename=%s content_type=%s",
        file.filename,
        file.content_type,
    )

    filename = file.filename or ""

    # ---------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # ---------------------------------------------------
    # STORE FILE
    # ---------------------------------------------------

    try:
        doc = store_pdf(
            upload_dir=settings.upload_dir,
            upload_file=file,
        )

        log.info("PDF stored successfully: %s", filename)

    except ValueError as exc:
        log.warning("Rejected invalid PDF upload: filename=%s", filename)
        raise _upload_validation_error(exc)
    except Exception:
        log.exception("Upload failed")
        raise HTTPException(status_code=500, detail="PDF upload failed.")

    return {
        "success": True,
        "document": doc,
    }


# ---------------------------------------------------
# FULL RAG INGESTION
# ---------------------------------------------------

@router.post("/upload-rag", response_model=UploadRagResponse)
async def upload_rag(file: UploadFile = File(...)):
    filename = file.filename or ""
    try:
        doc = store_pdf(
            upload_dir=settings.upload_dir,
            upload_file=file,
        )
        log.info("PDF uploaded for RAG: %s", filename)
    except ValueError as exc:
        log.warning("Rejected invalid PDF upload: filename=%s", filename)
        raise _upload_validation_error(exc)
    except Exception:
        log.exception("PDF upload failed")
        raise HTTPException(status_code=500, detail="PDF upload failed.")

    try:
        pdf_path = find_stored_pdf(settings.upload_dir, doc["id"])
        text = extract_pdf_text_from_path(pdf_path)
    except PDFExtractionError as exc:
        log.warning("PDF extraction failed: filename=%s", filename)
        remove_stored_pdf(settings.upload_dir, doc["id"])
        raise _extraction_error(exc)
    except (PDFPageCountExceededError, PDFTextLimitExceededError) as exc:
        log.warning("PDF extraction limit exceeded: filename=%s", filename)
        remove_stored_pdf(settings.upload_dir, doc["id"])
        raise _extraction_error(exc)
    except Exception:
        log.exception("PDF extraction failed")
        remove_stored_pdf(settings.upload_dir, doc["id"])
        raise HTTPException(status_code=500, detail="PDF text extraction failed.")

    if not text.strip():
        remove_stored_pdf(settings.upload_dir, doc["id"])
        raise HTTPException(
            status_code=422,
            detail="The PDF contains no selectable text. Scanned/image-only PDFs are not supported.",
        )

    try:
        from app.services.embedding_pipeline import (
            embed_and_store_pdf_chunks,
        )

        embed_result = embed_and_store_pdf_chunks(
            text=text,
            document=doc,
            chunk_size=1000,
            chunk_overlap=200,
        )
        if not embed_result.get("stored"):
            remove_stored_pdf(settings.upload_dir, doc["id"])
            raise HTTPException(
                status_code=422,
                detail="The PDF contains no selectable text to index.",
            )
        log.info("PDF indexed successfully: chunks=%s", embed_result["stored"])
    except HTTPException:
        raise
    except Exception:
        log.exception("Embedding pipeline failed")
        remove_stored_pdf(settings.upload_dir, doc["id"])
        raise HTTPException(
            status_code=503,
            detail="Document indexing is unavailable. Check the embedding model and Chroma service.",
        )

    return UploadRagResponse(
        document=doc,
        stored=embed_result.get("stored", 0),
        chunk_count=len(embed_result.get("chunks", [])),
        chunk_size=1000,
        chunk_overlap=200,
    )


# ---------------------------------------------------
# EXTRACT TEXT ONLY
# ---------------------------------------------------

@router.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):

    """
    Upload PDF →
    Extract raw text →
    Return chunks
    """

    filename = file.filename or ""

    if not filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # ---------------------------------------------------
    # STORE PDF
    # ---------------------------------------------------

    try:

        doc = store_pdf(
            upload_dir=settings.upload_dir,
            upload_file=file,
        )

    except ValueError as exc:
        log.warning("Rejected invalid PDF upload: filename=%s", filename)
        raise _upload_validation_error(exc)
    except Exception:
        log.exception("PDF upload failed")
        raise HTTPException(
            status_code=500,
            detail="PDF upload failed.",
        )

    try:
        pdf_path = find_stored_pdf(settings.upload_dir, doc["id"])
        text = extract_pdf_text_from_path(pdf_path)
    except (PDFPageCountExceededError, PDFTextLimitExceededError, PDFExtractionError) as exc:
        log.warning("PDF text extraction failed: filename=%s", filename)
        remove_stored_pdf(settings.upload_dir, doc["id"])
        raise _extraction_error(exc)
    except Exception:
        log.exception("PDF text extraction failed")
        remove_stored_pdf(settings.upload_dir, doc["id"])
        raise HTTPException(
            status_code=500,
            detail="PDF text extraction failed.",
        )

    if not text.strip():
        remove_stored_pdf(settings.upload_dir, doc["id"])
        raise HTTPException(
            status_code=422,
            detail="The PDF contains no selectable text. Scanned/image-only PDFs are not supported.",
        )

    # ---------------------------------------------------
    # CHUNK TEXT
    # ---------------------------------------------------

    chunks = chunk_text(
        text,
        chunk_size=1000,
        chunk_overlap=200,
    )

    # ---------------------------------------------------
    # RESPONSE
    # ---------------------------------------------------

    return ExtractTextResponse(
        document=doc,
        text=text,
        chunks=chunks,
        chunk_size=1000,
        chunk_overlap=200,
    ).model_dump()