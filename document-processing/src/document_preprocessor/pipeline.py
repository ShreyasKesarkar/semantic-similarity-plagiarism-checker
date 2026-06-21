"""
pipeline.py
-----------
Orchestrates the full document preprocessing flow:

    File (PDF/DOCX/TXT)
        -> validators (file type + basic sanity checks)
        -> extractor.extract_text()
        -> cleaner.clean_text()
        -> segmenter.segment_sentences()
        -> structured JSON-ready dict

This is the single function ("process_document") the rest of the
team should call -- whether that's wrapped in a FastAPI endpoint,
imported directly into the backend, or run from the CLI.

Per project requirements, this module's primary use case is comparing
TWO documents (Document A + Document B) for a teacher's plagiarism
report -- see process_document_pair() below. Documents may be of any
size / page count; nothing here imposes an artificial limit.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from . import extractor
from . import cleaner
from . import segmenter
from . import validators


def process_document(
    source: Union[str, bytes],
    filename: Optional[str] = None,
    document_id: Optional[str] = None,
    strip_citations: bool = False,
    min_sentence_words: int = 4,
    header_footer_min_repeats: int = 3,
    max_size_mb: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Run the full preprocessing pipeline on a single document.

    Args:
        source: EITHER a path (str) to a .pdf/.docx/.txt file on disk,
            OR raw file bytes (e.g. from a FastAPI UploadFile.read()) --
            no temp file required for the bytes case.
        filename: required when `source` is bytes, e.g. "essay.pdf"
            (used to detect file type and as the default document_id).
            Ignored when `source` is already a path.
        document_id: optional label for this document (e.g. "Document A").
            Defaults to the file's basename (path case) or `filename`
            (bytes case).
        strip_citations: forwarded to cleaner.clean_text()
        min_sentence_words: forwarded to segmenter.segment_sentences()
        header_footer_min_repeats: forwarded to cleaner.clean_text()
        max_size_mb: optional upload size cap in megabytes. Off by
            default (documents may be any size per project requirements).

    Raises:
        UnsupportedFileTypeError: file isn't .pdf, .docx, or .txt
        ValidationError: file is empty, or exceeds max_size_mb (if set)
        ExtractionError: file is the right type but couldn't be parsed
        FileNotFoundError: a path was given but doesn't exist

    Returns:
        A dict matching the schema described in README.md, e.g.:

        {
            "document_id": "essay_studentA.pdf",
            "source_path": "/path/to/essay_studentA.pdf",  // null if bytes were passed
            "file_type": "pdf",
            "extraction_metadata": {...},
            "raw_char_count": 5421,
            "cleaned_char_count": 5310,
            "sentence_count": 48,
            "sentences": ["...", "...", ...],
            "processed_at": "2026-06-21T10:15:00+00:00"
        }
    """
    is_bytes = isinstance(source, (bytes, bytearray))

    # --- Validation (fail fast, before any parsing work) ---
    validators.validate_not_empty(source)
    if is_bytes:
        validators.validate_max_size(len(source), max_size_mb=max_size_mb)
    else:
        validators.validate_max_size(os.path.getsize(source), max_size_mb=max_size_mb)

    raw_text, extraction_metadata = extractor.extract_text(source, filename=filename)

    cleaned_text = cleaner.clean_text(
        raw_text,
        strip_citations=strip_citations,
        header_footer_min_repeats=header_footer_min_repeats,
    )

    sentences = segmenter.segment_sentences(
        cleaned_text,
        min_words=min_sentence_words,
    )

    default_id = filename if is_bytes else os.path.basename(source)

    result: Dict[str, Any] = {
        "document_id": document_id or default_id,
        "source_path": None if is_bytes else os.path.abspath(source),
        "file_type": extraction_metadata.get("file_type"),
        "extraction_metadata": extraction_metadata,
        "raw_char_count": len(raw_text),
        "cleaned_char_count": len(cleaned_text),
        "sentence_count": len(sentences),
        "sentences": sentences,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }
    return result


def process_document_to_json(
    source: Union[str, bytes],
    output_path: Optional[str] = None,
    **kwargs: Any,
) -> str:
    """
    Convenience wrapper: run process_document() and write the result
    as a JSON file. Returns the JSON string either way.

    If output_path is None, the JSON is just returned (not written
    to disk) -- handy for quick testing or for callers (like a future
    FastAPI endpoint) that want to return it directly in a response.
    """
    result = process_document(source, **kwargs)
    json_str = json.dumps(result, indent=2, ensure_ascii=False)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_str)

    return json_str


def process_document_pair(
    source_a: Union[str, bytes],
    source_b: Union[str, bytes],
    filename_a: Optional[str] = None,
    filename_b: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    The system's core use case: a teacher compares TWO student
    documents ("Document A" + "Document B") for a plagiarism report.

    Each of source_a / source_b can independently be a file path or raw
    bytes (e.g. one saved on disk, one freshly uploaded -- doesn't matter),
    and independently PDF, DOCX, or TXT.

    Returns a dict with both processed documents, ready to be handed
    to the SBERT embedding step:

        {"document_a": {...}, "document_b": {...}}
    """
    return {
        "document_a": process_document(
            source_a, filename=filename_a, document_id="Document A", **kwargs
        ),
        "document_b": process_document(
            source_b, filename=filename_b, document_id="Document B", **kwargs
        ),
    }
