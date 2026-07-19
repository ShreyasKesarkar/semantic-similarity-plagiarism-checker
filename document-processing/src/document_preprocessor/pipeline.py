"""
pipeline.py
-----------
Orchestrates the full document preprocessing flow:

    File (PDF / DOCX / TXT)
        → validators      (type check, empty check)
        → extractor       (raw text + file metadata)
        → cleaner         (clean prose + structure metadata: title, headings)
        → segmenter       (sentence list)
        → result dict     (handed to SBERT module)

Updated output schema based on SBERT teammate feedback:
    - "title" field added   (document title, kept as metadata, NOT sent to SBERT)
    - "headings" field added (section headings, kept as metadata, NOT sent to SBERT)
    - "sentences" contains ONLY real content sentences — clean input for SBERT
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from . import extractor
from .cleaner import clean_and_extract_structure
from . import segmenter
from . import validators


def process_document(
    source: Union[str, bytes],
    filename: Optional[str] = None,
    document_id: Optional[str] = None,
    strip_citations: bool = False,
    min_sentence_words: int = 5,
    header_footer_min_repeats: int = 2,
    max_size_mb: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Run the full preprocessing pipeline on a single document.

    Args:
        source: file path (str) OR raw bytes from a FastAPI UploadFile
        filename: required when source is bytes (e.g. "essay.pdf")
        document_id: label for this document. Defaults to filename.
        strip_citations: remove [12]-style citations (off by default)
        min_sentence_words: drop sentences shorter than this (default 5)
        header_footer_min_repeats: repeats threshold for header detection (default 2)
        max_size_mb: optional file size cap (None = no limit, per project spec)

    Returns:
        {
            "document_id": "Document A",
            "source_path": "/path/to/file.pdf",   # null if bytes were passed
            "file_type": "pdf",
            "title": "Impact of Climate Change...", # detected document title
            "headings": ["Introduction", "3.1 ..."],# section headings (metadata only)
            "extraction_metadata": { "num_pages": 5, ... },
            "raw_char_count": 5421,
            "cleaned_char_count": 5200,
            "sentence_count": 48,
            "sentences": ["...", "..."],            # ← SBERT consumes this only
            "processed_at": "2026-..."
        }
    """
    is_bytes = isinstance(source, (bytes, bytearray))

    # --- Validation ---
    validators.validate_not_empty(source)
    size = len(source) if is_bytes else os.path.getsize(source)
    validators.validate_max_size(size, max_size_mb=max_size_mb)

    # --- Extraction ---
    raw_text, extraction_metadata = extractor.extract_text(source, filename=filename)

    # --- Cleaning (now also returns title + headings) ---
    cleaned_text, structure = clean_and_extract_structure(
        raw_text,
        strip_citations=strip_citations,
        header_footer_min_repeats=header_footer_min_repeats,
    )

    # --- Segmentation ---
    sentences = segmenter.segment_sentences(cleaned_text, min_words=min_sentence_words)

    default_id = filename if is_bytes else os.path.basename(source)

    return {
        "document_id": document_id or default_id,
        "source_path": None if is_bytes else os.path.abspath(source),
        "file_type": extraction_metadata.get("file_type"),
        # --- NEW fields (based on SBERT teammate feedback) ---
        "title": structure.get("title"),
        "headings": structure.get("headings", []),
        # --- existing fields ---
        "extraction_metadata": extraction_metadata,
        "raw_char_count": len(raw_text),
        "cleaned_char_count": len(cleaned_text),
        "sentence_count": len(sentences),
        "sentences": sentences,   # ← the only thing SBERT needs
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }


def process_document_to_json(
    source: Union[str, bytes],
    output_path: Optional[str] = None,
    **kwargs: Any,
) -> str:
    """Run process_document() and optionally save result to a JSON file."""
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
    Core use case: compare two student documents for a plagiarism report.

    Processes each document independently, then returns both results
    under "document_a" and "document_b" keys. Sentences are never
    mixed between documents.

    The SBERT module should use:
        result["document_a"]["sentences"]
        result["document_b"]["sentences"]
    """
    return {
        "document_a": process_document(
            source_a, filename=filename_a, document_id="Document A", **kwargs
        ),
        "document_b": process_document(
            source_b, filename=filename_b, document_id="Document B", **kwargs
        ),
    }
