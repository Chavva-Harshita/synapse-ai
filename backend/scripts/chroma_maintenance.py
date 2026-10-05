from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import unicodedata
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any

import chromadb
import numpy as np


COLLECTION_NAME = "synapse_ai_docs"


def _metadata_name_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(character for character in normalized if character.isalnum())


def _stored_document_names(upload_dir: Path) -> dict[str, str]:
    names: dict[str, str] = {}
    if not upload_dir.is_dir():
        return names
    for path in upload_dir.glob("*.pdf"):
        document_id, separator, name = path.name.partition("__")
        if separator and path.is_file():
            names.setdefault(document_id, name)
    return names


def _read_all_records(collection: Any) -> dict[str, Any]:
    return collection.get(include=["documents", "metadatas", "embeddings"])


def _build_plan(records: dict[str, Any], upload_dir: Path) -> list[dict[str, Any]]:
    groups: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    stored_names = _stored_document_names(upload_dir)

    for record_id, text, metadata, embedding in zip(
        records["ids"],
        records["documents"],
        records["metadatas"],
        records["embeddings"],
    ):
        metadata = metadata or {}
        document_id = metadata.get("document_id")
        chunk_index = metadata.get("chunk_index")
        if (
            not isinstance(document_id, str)
            or not document_id
            or not isinstance(chunk_index, int)
            or isinstance(chunk_index, bool)
            or not isinstance(text, str)
            or embedding is None
        ):
            raise ValueError(
                f"Cannot safely process Chroma row {record_id!r}: "
                "document_id, chunk_index, text, or embedding is missing."
            )
        groups[(document_id, chunk_index)].append(
            {
                "id": record_id,
                "text": text,
                "metadata": dict(metadata),
                "embedding": np.asarray(embedding, dtype=np.float32),
            }
        )

    existing_ids = set(records["ids"])
    plan: list[dict[str, Any]] = []
    for (document_id, chunk_index), rows in sorted(groups.items()):
        texts = {row["text"] for row in rows}
        if len(texts) != 1:
            raise ValueError(
                f"Conflicting text for document {document_id}, chunk {chunk_index}; "
                "no rows were changed."
            )
        metadata_without_name = {
            json.dumps(
                {
                    key: value
                    for key, value in row["metadata"].items()
                    if key != "document_name"
                },
                sort_keys=True,
            )
            for row in rows
        }
        if len(metadata_without_name) != 1:
            raise ValueError(
                f"Conflicting metadata for document {document_id}, chunk {chunk_index}; "
                "no rows were changed."
            )

        embeddings = [row["embedding"] for row in rows]
        if any(
            embedding.shape != embeddings[0].shape
            or not np.allclose(embedding, embeddings[0], rtol=1e-5, atol=1e-6)
            for embedding in embeddings[1:]
        ):
            raise ValueError(
                f"Conflicting embeddings for document {document_id}, chunk {chunk_index}; "
                "no rows were changed."
            )

        expected_name = stored_names.get(document_id)
        matching_rows = [
            row
            for row in rows
            if expected_name
            and isinstance(row["metadata"].get("document_name"), str)
            and _metadata_name_key(row["metadata"]["document_name"])
            == _metadata_name_key(expected_name)
        ]
        candidates = matching_rows or rows
        canonical = min(candidates, key=lambda row: row["id"])
        target_id = f"{document_id}:{chunk_index}"
        if target_id in existing_ids and all(
            row["id"] != target_id for row in rows
        ):
            raise ValueError(
                f"Stable ID collision for document {document_id}, chunk {chunk_index}; "
                "no rows were changed."
            )
        stable_row = next(
            (row for row in rows if row["id"] == target_id),
            None,
        )
        if stable_row and (
            stable_row["text"] != canonical["text"]
            or stable_row["metadata"] != canonical["metadata"]
            or stable_row["embedding"].shape != canonical["embedding"].shape
            or not np.allclose(
                stable_row["embedding"],
                canonical["embedding"],
                rtol=1e-5,
                atol=1e-6,
            )
        ):
            raise ValueError(
                f"Existing stable ID conflicts for document {document_id}, "
                f"chunk {chunk_index}; no rows were changed."
            )

        plan.append(
            {
                "target_id": target_id,
                "document_id": document_id,
                "chunk_index": chunk_index,
                "text": canonical["text"],
                "metadata": canonical["metadata"],
                "embedding": canonical["embedding"],
                "source_ids": sorted(row["id"] for row in rows),
                "source_row_count": len(rows),
            }
        )
    return plan


def _backup_database(source: Path, backup: Path) -> None:
    source = source.resolve()
    backup = backup.resolve()
    if not (source / "chroma.sqlite3").is_file():
        raise ValueError(f"Chroma database not found at {source}")
    if backup == source or source in backup.parents or backup in source.parents:
        raise ValueError("The backup directory must be separate from the Chroma directory.")
    if backup.exists():
        raise FileExistsError(f"Backup directory already exists: {backup}")
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, backup)
    source_files = {
        path.relative_to(source): path
        for path in source.rglob("*")
        if path.is_file()
    }
    backup_files = {
        path.relative_to(backup): path
        for path in backup.rglob("*")
        if path.is_file()
    }
    if set(source_files) != set(backup_files):
        raise RuntimeError(f"Backup verification failed for {backup}")
    for relative_path, source_file in source_files.items():
        backup_file = backup_files[relative_path]
        if source_file.stat().st_size != backup_file.stat().st_size:
            raise RuntimeError(f"Backup size mismatch for {relative_path}")
        source_hash = hashlib.sha256(source_file.read_bytes()).digest()
        backup_hash = hashlib.sha256(backup_file.read_bytes()).digest()
        if source_hash != backup_hash:
            raise RuntimeError(f"Backup checksum mismatch for {relative_path}")


def _restore_database(source: Path, target: Path) -> Path:
    source = source.resolve()
    target = target.resolve()
    if not (source / "chroma.sqlite3").is_file():
        raise ValueError(f"Backup database not found at {source}")
    if source == target or source in target.parents or target in source.parents:
        raise ValueError("The restore source and target must be separate directories.")

    restore_stage = target.with_name(f"{target.name}.restore-{uuid.uuid4().hex}")
    previous_target = target.with_name(f"{target.name}.before-restore-{uuid.uuid4().hex}")
    shutil.copytree(source, restore_stage)
    if target.exists():
        target.rename(previous_target)
    try:
        restore_stage.rename(target)
    except Exception:
        if previous_target.exists() and not target.exists():
            previous_target.rename(target)
        if restore_stage.exists():
            shutil.rmtree(restore_stage)
        raise
    return previous_target


def _verify_plan(collection: Any, plan: list[dict[str, Any]]) -> None:
    expected_ids = {record["target_id"] for record in plan}
    actual = collection.get(include=["documents", "metadatas", "embeddings"])
    if set(actual["ids"]) != expected_ids:
        raise RuntimeError("Post-cleanup Chroma IDs differ from the verified plan.")

    rows = {
        record_id: (text, metadata or {}, np.asarray(embedding, dtype=np.float32))
        for record_id, text, metadata, embedding in zip(
            actual["ids"],
            actual["documents"],
            actual["metadatas"],
            actual["embeddings"],
        )
    }
    for expected in plan:
        text, metadata, embedding = rows[expected["target_id"]]
        if text != expected["text"] or metadata != expected["metadata"]:
            raise RuntimeError(
                f"Post-cleanup content or metadata mismatch for {expected['target_id']}."
            )
        if embedding.shape != expected["embedding"].shape or not np.allclose(
            embedding,
            expected["embedding"],
            rtol=1e-5,
            atol=1e-6,
        ):
            raise RuntimeError(
                f"Post-cleanup embedding mismatch for {expected['target_id']}."
            )


def _apply_plan(collection: Any, plan: list[dict[str, Any]], original_ids: list[str]) -> None:
    existing_ids = set(original_ids)
    new_records = [record for record in plan if record["target_id"] not in existing_ids]
    if new_records:
        collection.add(
            ids=[record["target_id"] for record in new_records],
            documents=[record["text"] for record in new_records],
            metadatas=[record["metadata"] for record in new_records],
            embeddings=[record["embedding"].tolist() for record in new_records],
        )

    _verify_plan_subset(collection, new_records)
    desired_ids = {record["target_id"] for record in plan}
    remove_ids = sorted(existing_ids - desired_ids)
    if remove_ids:
        collection.delete(ids=remove_ids)

    _verify_plan(collection, plan)


def _verify_plan_subset(collection: Any, records: list[dict[str, Any]]) -> None:
    if not records:
        return
    actual = collection.get(
        ids=[record["target_id"] for record in records],
        include=["documents", "metadatas", "embeddings"],
    )
    if set(actual["ids"]) != {record["target_id"] for record in records}:
        raise RuntimeError("Chroma did not persist all canonical chunk records.")
    rows = {
        record_id: (text, metadata or {}, np.asarray(embedding, dtype=np.float32))
        for record_id, text, metadata, embedding in zip(
            actual["ids"],
            actual["documents"],
            actual["metadatas"],
            actual["embeddings"],
        )
    }
    for expected in records:
        text, metadata, embedding = rows[expected["target_id"]]
        if text != expected["text"] or metadata != expected["metadata"]:
            raise RuntimeError(
                f"Canonical chunk validation failed for {expected['target_id']}."
            )
        if embedding.shape != expected["embedding"].shape or not np.allclose(
            embedding,
            expected["embedding"],
            rtol=1e-5,
            atol=1e-6,
        ):
            raise RuntimeError(
                f"Canonical embedding validation failed for {expected['target_id']}."
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Safely deduplicate legacy Synapse Chroma chunks."
    )
    parser.add_argument("--persist-dir", type=Path, default=Path("./chroma_db"))
    parser.add_argument("--upload-dir", type=Path, default=Path("./uploads"))
    parser.add_argument("--apply", action="store_true", help="Back up and apply the plan.")
    parser.add_argument("--backup-dir", type=Path)
    parser.add_argument("--restore-from", type=Path)
    args = parser.parse_args()

    persist_dir = args.persist_dir.resolve()
    if args.restore_from:
        if args.apply or args.backup_dir:
            parser.error("--restore-from cannot be combined with --apply or --backup-dir.")
        preserved = _restore_database(args.restore_from, persist_dir)
        print(f"Restored Chroma database from {args.restore_from.resolve()}")
        if preserved.exists():
            print(f"Previous database preserved at {preserved}")
        return 0

    if args.apply and not args.backup_dir:
        parser.error("--apply requires --backup-dir outside the Chroma directory.")
    if args.backup_dir and not args.apply:
        parser.error("--backup-dir is only valid with --apply.")

    if args.apply:
        backup_dir = args.backup_dir.resolve()
        _backup_database(persist_dir, backup_dir)
        print(f"Verified pre-change backup created at {backup_dir}")

    client = chromadb.PersistentClient(path=str(persist_dir))
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception as exc:
        raise RuntimeError(f"Could not open collection {COLLECTION_NAME!r}.") from exc

    records = _read_all_records(collection)
    plan = _build_plan(records, args.upload_dir.resolve())
    extra_rows = len(records["ids"]) - len(plan)
    document_ids = {record["document_id"] for record in plan}
    stable_rekeys = sum(
        record["target_id"] not in record["source_ids"] for record in plan
    )
    print(
        json.dumps(
            {
                "collection": COLLECTION_NAME,
                "rows_before": len(records["ids"]),
                "documents": len(document_ids),
                "unique_chunks": len(plan),
                "duplicate_rows_to_remove": extra_rows,
                "canonical_ids_to_stabilize": stable_rekeys,
                "mode": "apply" if args.apply else "dry-run",
            },
            indent=2,
        )
    )
    if not args.apply:
        return 0

    _apply_plan(collection, plan, records["ids"])
    print(
        json.dumps(
            {
                "rows_after": collection.count(),
                "documents_after": len(document_ids),
                "unique_chunks_after": len(plan),
                "backup": str(backup_dir),
                "status": "verified",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
