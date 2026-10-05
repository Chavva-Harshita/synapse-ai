import os
from pathlib import Path

from dotenv import load_dotenv # type: ignore


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env", override=False)

DEFAULT_CORS_ALLOWED_ORIGINS = (
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:5176",
)


def _positive_int_setting(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    try:
        value = default if raw_value is None else int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


class Settings:
    upload_dir = os.getenv("SYNAPSE_UPLOAD_DIR", "./uploads")
    chroma_dir = os.getenv("SYNAPSE_CHROMA_DIR", "./chroma_db")
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    # This was the Ollama client's existing fallback and is available in the current local setup.
    ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b").strip()
    cors_allowed_origins = tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOWED_ORIGINS",
            ",".join(DEFAULT_CORS_ALLOWED_ORIGINS),
        ).split(",")
        if origin.strip()
    )
    max_pdf_upload_bytes = _positive_int_setting(
        "MAX_PDF_UPLOAD_BYTES",
        25 * 1024 * 1024,
    )
    max_pdf_pages = _positive_int_setting("MAX_PDF_PAGES", 500)
    max_pdf_extracted_chars = _positive_int_setting(
        "MAX_PDF_EXTRACTED_CHARS",
        5_000_000,
    )


settings = Settings()
