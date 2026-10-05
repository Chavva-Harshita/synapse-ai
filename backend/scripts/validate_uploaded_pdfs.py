from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from uuid import uuid4

import chromadb
from langchain_chroma import Chroma

from app.core.config import settings
from app.services.ollama_client import OllamaError
from app.services.pdf_text_extractor import extract_pdf_text_from_path
from app.services.retriever import MAX_CHROMA_DISTANCE
from app.services.response_generation import generate_grounded_reply
from app.services.text_chunker import chunk_text
from app.services.vector_store import EMBEDDING_MODEL_NAME, _get_embedding_function


def _remove_private_fields(samples: list[dict]) -> None:
    for sample in samples:
        sample.pop("chunks", None)
        sample.pop("document_id", None)
        sample.pop("sha256", None)


def validate_uploaded_pdfs(upload_dir: Path) -> dict:
    paths = sorted(upload_dir.glob("*.pdf"))
    if not paths:
        return {"status": "no_samples", "documents": []}

    samples: list[dict] = []
    seen_hashes: set[str] = set()
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in seen_hashes:
            continue
        seen_hashes.add(digest)
        sample: dict = {
            "sample": len(samples) + 1,
            "bytes": path.stat().st_size,
            "sha256": digest,
        }
        try:
            from PyPDF2 import PdfReader # type: ignore

            page_count = len(PdfReader(str(path), strict=False).pages)
            text = extract_pdf_text_from_path(str(path))
        except Exception as exc:  # noqa: BLE001
            sample.update(
                {
                    "status": "extraction_failed",
                    "error_type": type(exc).__name__,
                }
            )
            samples.append(sample)
            continue

        sample.update(
            {
                "pages": page_count,
                "extracted_characters": len(text),
                "heading_like_lines": sum(
                    bool(re.fullmatch(r"[A-Z0-9][A-Z0-9 .:&/-]{2,80}", line.strip()))
                    for line in text.splitlines()
                ),
                "table_like_lines": sum(
                    "|" in line or bool(re.search(r"\S {3,}\S", line))
                    for line in text.splitlines()
                ),
            }
        )
        if not text.strip():
            sample.update(
                {
                    "status": "unsupported_image_only_or_empty",
                    "ocr_attempted": False,
                }
            )
        else:
            sample["document_id"] = str(uuid4())
            sample["chunks"] = chunk_text(text, chunk_size=1000, chunk_overlap=200)
            sample["status"] = "extracted"
        samples.append(sample)

    indexable = [sample for sample in samples if sample["status"] == "extracted"]
    if not indexable:
        _remove_private_fields(samples)
        return {"status": "failed", "documents": samples}

    vector_store = Chroma(
        client=chromadb.EphemeralClient(),
        collection_name=f"synapse-pdf-smoke-{uuid4().hex}",
        embedding_function=_get_embedding_function(EMBEDDING_MODEL_NAME),
    )
    texts = []
    metadatas = []
    identifiers = []
    expected: dict[str, str] = {}
    for sample in indexable:
        for chunk_index, chunk in enumerate(sample["chunks"]):
            chunk_id = f"{sample['document_id']}:{chunk_index}"
            texts.append(chunk)
            metadatas.append(
                {
                    "document_id": sample["document_id"],
                    "chunk_index": chunk_index,
                }
            )
            identifiers.append(chunk_id)
        expected[sample["document_id"]] = f"{sample['document_id']}:0"
    vector_store.add_texts(texts=texts, metadatas=metadatas, ids=identifiers)

    for sample in indexable:
        document_id = sample["document_id"]
        query = sample["chunks"][0]
        matches = vector_store.similarity_search_with_score(
            query,
            k=1,
            filter={"document_id": document_id},
        )
        if not matches:
            sample.update(
                {
                    "status": "retrieval_failed",
                    "retrieval_found_expected_chunk": False,
                }
            )
            continue

        document, distance = matches[0]
        scoped = document.metadata.get("document_id") == document_id
        correct_chunk = (
            scoped and document.metadata.get("chunk_index") == 0
        )
        sample.update(
            {
                "retrieval_distance": float(distance),
                "retrieval_found_expected_chunk": correct_chunk,
                "document_scope_isolated": scoped,
                "within_current_distance_cutoff": (
                    float(distance) <= MAX_CHROMA_DISTANCE
                ),
            }
        )
        try:
            result = generate_grounded_reply(
                question="Summarize the provided excerpt in one sentence.",
                retrieved_chunks=[
                    {
                        "source_text": document.page_content,
                        "metadata": dict(document.metadata),
                    }
                ],
            )
            sample["grounded_response_received"] = bool(result.reply.strip())
            sample["status"] = (
                "passed"
                if correct_chunk and scoped and result.reply.strip()
                else "failed"
            )
        except OllamaError as exc:
            sample.update(
                {
                    "status": "ollama_unavailable",
                    "grounded_response_received": False,
                    "error_type": type(exc).__name__,
                }
            )

    failed_statuses = {
        "extraction_failed",
        "retrieval_failed",
        "failed",
        "ollama_unavailable",
    }
    failed = any(sample["status"] in failed_statuses for sample in samples)
    _remove_private_fields(samples)
    return {
        "status": "failed" if failed else "passed",
        "unique_pdf_samples": len(samples),
        "duplicates_skipped": len(paths) - len(samples),
        "ephemeral_index_chunks": len(identifiers),
        "documents": samples,
    }


if __name__ == "__main__":
    result = validate_uploaded_pdfs(Path(settings.upload_dir))
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "passed" else 1)
