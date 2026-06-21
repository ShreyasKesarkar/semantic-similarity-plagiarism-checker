"""
document_preprocessor
======================
Document Processing module for the AI Plagiarism Detection System.

Scope (per project spec):
    - Accepts PDF, DOCX, and TXT files
    - Validates file format (rejects anything else)
    - Extracts textual content
    - Removes noise: formatting artifacts, repeated headers/footers,
      page numbers, optionally citations
    - Performs sentence segmentation
    - Generates document metadata
    - Produces structured, sentence-level output ready for the
      SBERT-based similarity engine (built by another team member)

Handles documents of any size (no artificial page/length limit), and
accepts input either as a file path or as raw in-memory bytes (for a
direct, temp-file-free handoff from a FastAPI UploadFile).

Quick start
-----------
    from document_preprocessor import process_document_pair

    result = process_document_pair("essayA.pdf", "essayB.docx")
    result["document_a"]["sentences"]   # -> feed into SBERT
    result["document_b"]["sentences"]

See README.md for the full input/output contract and integration notes.
"""

from .pipeline import (
    process_document,
    process_document_to_json,
    process_document_pair,
)
from .extractor import (
    extract_text,
    extract_text_from_pdf,
    extract_text_from_pdf_bytes,
    extract_text_from_docx,
    extract_text_from_docx_bytes,
    extract_text_from_txt,
    extract_text_from_txt_bytes,
)
from .cleaner import clean_text
from .segmenter import segment_sentences
from .validators import (
    SUPPORTED_EXTENSIONS,
    is_supported_filename,
    validate_filename,
)
from .exceptions import (
    UnsupportedFileTypeError,
    ExtractionError,
    ValidationError,
)

__all__ = [
    # pipeline (most teammates only need these three)
    "process_document",
    "process_document_to_json",
    "process_document_pair",
    # extraction
    "extract_text",
    "extract_text_from_pdf",
    "extract_text_from_pdf_bytes",
    "extract_text_from_docx",
    "extract_text_from_docx_bytes",
    "extract_text_from_txt",
    "extract_text_from_txt_bytes",
    # cleaning / segmentation
    "clean_text",
    "segment_sentences",
    # validation
    "SUPPORTED_EXTENSIONS",
    "is_supported_filename",
    "validate_filename",
    # exceptions
    "UnsupportedFileTypeError",
    "ExtractionError",
    "ValidationError",
]

__version__ = "0.2.0"
