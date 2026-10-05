from __future__ import annotations

import json
from uuid import uuid4

import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.services.retriever import MAX_CHROMA_DISTANCE


PASSAGES = [
    {
        "id": "field-calendar",
        "document_id": "field-notes",
        "text": (
            "The Willow Marsh research station recorded blue heron sightings "
            "from April through June. Field counts were conducted at dawn near "
            "the north reed beds."
        ),
    },
    {
        "id": "visitor-information",
        "document_id": "field-notes",
        "text": (
            "The visitor desk for the Willow Marsh research station is located "
            "in Port Alder. Volunteer training takes place on the first Monday "
            "of May."
        ),
    },
    {
        "id": "heron-reference",
        "document_id": "bird-guide",
        "text": (
            "Blue herons are tall wading birds with long necks and pointed bills. "
            "They often hunt for fish in shallow wetlands."
        ),
    },
]

CASES = [
    {
        "query": "During which months did staff track blue heron sightings?",
        "supported": True,
        "evidence": "April through June",
    },
    {
        "query": "At what time were the marsh team's bird counts conducted?",
        "supported": True,
        "evidence": "at dawn",
    },
    {
        "query": "Where can someone find the visitor desk?",
        "supported": True,
        "evidence": "Port Alder",
    },
    {
        "query": "On which day does volunteer training take place?",
        "supported": True,
        "evidence": "first Monday of May",
    },
    {
        "query": "How many blue herons were recorded last year?",
        "supported": False,
        "evidence": None,
    },
    {
        "query": "What is the station's annual operating budget?",
        "supported": False,
        "evidence": None,
    },
    {
        "query": "Who founded the Willow Marsh research station?",
        "supported": False,
        "evidence": None,
    },
    {
        "query": "How long do blue herons live in the wild?",
        "supported": False,
        "evidence": None,
    },
    {
        "query": "Does Port Alder have visitor parking?",
        "supported": False,
        "evidence": None,
    },
]


def evaluate(threshold: float = MAX_CHROMA_DISTANCE) -> dict:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    store = Chroma(
        client=chromadb.EphemeralClient(),
        collection_name=f"synapse-evaluation-{uuid4().hex}",
        embedding_function=embeddings,
    )
    store.add_texts(
        texts=[passage["text"] for passage in PASSAGES],
        metadatas=[
            {
                "document_id": passage["document_id"],
                "chunk_id": passage["id"],
            }
            for passage in PASSAGES
        ],
        ids=[passage["id"] for passage in PASSAGES],
    )

    results = []
    for case in CASES:
        matches = store.similarity_search_with_score(case["query"], k=1)
        if matches:
            document, distance = matches[0]
            chunk_id = document.metadata["chunk_id"]
            distance = float(distance)
            relevant = (
                case["supported"]
                and case["evidence"] is not None
                and case["evidence"].casefold() in document.page_content.casefold()
            )
        else:
            document = None
            distance = None
            chunk_id = None
            relevant = False

        results.append(
            {
                "query": case["query"],
                "expected_supported": case["supported"],
                "retrieved_chunk_id": chunk_id,
                "retrieved_chunk": document.page_content if document else None,
                "distance": distance,
                "retrieved_chunk_relevant": relevant,
                "accepted_at_threshold": (
                    distance is not None and distance <= threshold
                ),
            }
        )

    return {
        "threshold": threshold,
        "cases": results,
        "supported_queries": sum(case["supported"] for case in CASES),
        "unsupported_queries": sum(not case["supported"] for case in CASES),
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
