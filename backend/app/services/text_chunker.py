from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """Chunk text into overlapping segments.

    Uses LangChain's RecursiveCharacterTextSplitter when available.
    Falls back to a small local splitter to keep the service robust.
    """

    text = text or ""
    if not text.strip():
        return []

    try:
        # Prefer LangChain (requested)
        from langchain_text_splitters import RecursiveCharacterTextSplitter # type: ignore

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return splitter.split_text(text)
    except Exception:
        # Minimal fallback (character-based sliding window)
        step = max(chunk_size - chunk_overlap, 1)
        chunks: list[str] = []
        i = 0
        while i < len(text):
            chunks.append(text[i:i + chunk_size])
            if i + chunk_size >= len(text):
                break
            i += step
        return [c.strip() for c in chunks if c.strip()]

