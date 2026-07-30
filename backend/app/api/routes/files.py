import os
import logging

from fastapi import APIRouter, File, HTTPException, UploadFile # type: ignore

from app.core.config import settings
from app.services.file_service import store_pdf
from app.services.pdf_text_extractor import extract_pdf_text_from_path
from app.services.text_chunker import chunk_text

from app.api.routes.upload_models import ExtractTextResponse
from app.api.routes.upload_rag_models import UploadRagResponse


# ---------------------------------------------------
# LOGGER
# ---------------------------------------------------

log = logging.getLogger(__name__)


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

    except ValueError as e:

        log.error("Validation error: %s", str(e))

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        log.exception("Upload failed")

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {e}"
        )

    return {
        "success": True,
        "document": doc,
    }


# ---------------------------------------------------
# FULL RAG INGESTION
# ---------------------------------------------------

@router.post("/upload-rag", response_model=UploadRagResponse)
async def upload_rag(file: UploadFile = File(...)):

    """
    Upload PDF →
    Extract text →
    Chunk →
    Embed →
    Store in ChromaDB
    """

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
    # STORE PDF
    # ---------------------------------------------------

    try:

        doc = store_pdf(
            upload_dir=settings.upload_dir,
            upload_file=file,
        )

        log.info("PDF uploaded for RAG: %s", filename)

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        log.exception("PDF upload failed")

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {e}"
        )

    # ---------------------------------------------------
    # LOCATE SAVED FILE
    # ---------------------------------------------------

    prefix = f"{doc['id']}__"

    pdf_path = None

    for name in os.listdir(settings.upload_dir):

        if (
            name.startswith(prefix)
            and name.lower().endswith(".pdf")
        ):

            pdf_path = os.path.join(
                settings.upload_dir,
                name,
            )

            break

    # ---------------------------------------------------
    # FILE NOT FOUND
    # ---------------------------------------------------

    if not pdf_path:

        raise HTTPException(
            status_code=500,
            detail="Stored PDF could not be located"
        )

    # ---------------------------------------------------
    # EXTRACT PDF TEXT
    # ---------------------------------------------------

    try:

        text = extract_pdf_text_from_path(pdf_path)

        log.info("PDF text extracted successfully")

    except Exception as e:

        log.exception("PDF extraction failed")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse PDF: {e}"
        )

    # ---------------------------------------------------
    # CHUNKING
    # ---------------------------------------------------

    try:

        chunks = chunk_text(
            text,
            chunk_size=1000,
            chunk_overlap=200,
        )

        log.info("Chunking completed: %s chunks", len(chunks))

    except Exception as e:

        log.exception("Chunking failed")

        raise HTTPException(
            status_code=500,
            detail=f"Chunking failed: {e}"
        )

    # ---------------------------------------------------
    # EMBEDDING + VECTOR STORAGE
    # ---------------------------------------------------

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

        log.info(
            "Embeddings stored successfully: %s chunks",
            len(embed_result.get("chunks", []))
        )

    except Exception as e:

        log.exception("Embedding pipeline failed")

        raise HTTPException(
            status_code=500,
            detail=f"Embedding pipeline failed: {e}"
        )

    # ---------------------------------------------------
    # SUCCESS RESPONSE
    # ---------------------------------------------------

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

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {e}"
        )

    # ---------------------------------------------------
    # LOCATE FILE
    # ---------------------------------------------------

    prefix = f"{doc['id']}__"

    pdf_path = None

    for name in os.listdir(settings.upload_dir):

        if (
            name.startswith(prefix)
            and name.lower().endswith(".pdf")
        ):

            pdf_path = os.path.join(
                settings.upload_dir,
                name,
            )

            break

    if not pdf_path:

        raise HTTPException(
            status_code=500,
            detail="Stored PDF not found"
        )

    # ---------------------------------------------------
    # EXTRACT TEXT
    # ---------------------------------------------------

    try:

        text = extract_pdf_text_from_path(pdf_path)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Text extraction failed: {e}"
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