"""
extractor.py
------------
Responsible for pulling raw text out of academic documents.

Supports:
    - PDF   (via PyMuPDF / fitz)
    - DOCX  (via python-docx)
    - TXT   (plain text, with encoding fallback)

Two ways to hand it a document:
    1. A file path (str)   -- e.g. a file already saved on disk
    2. Raw bytes            -- e.g. straight from a FastAPI UploadFile,
                                no temp file needed

Design notes:
    - Each extractor returns a tuple: (full_text, metadata_dict)
    - metadata_dict captures things downstream steps / the report
      generator might want (page count, paragraph count, etc.)
    - We deliberately keep extraction "dumb" (just get the text out).
      All cleaning/normalization happens in cleaner.py so each module
      has a single responsibility.
    - File type validation is delegated to validators.py so there's
      one source of truth for "what's a supported file".
"""

from __future__ import annotations

import io
import os
from typing import Tuple, Dict, Any, Optional, Union

import fitz  # PyMuPDF
import docx  # python-docx

from .exceptions import UnsupportedFileTypeError, ExtractionError
from .validators import validate_filename

# Re-exported here too for convenience / backwards compatibility, since
# earlier versions of this module defined these exceptions itself.
__all__ = [
    "extract_text",
    "extract_text_from_pdf",
    "extract_text_from_pdf_bytes",
    "extract_text_from_docx",
    "extract_text_from_docx_bytes",
    "extract_text_from_txt",
    "extract_text_from_txt_bytes",
    "UnsupportedFileTypeError",
    "ExtractionError",
]

# Encodings tried in order when decoding plain text files. Covers the
# vast majority of real-world student submissions (UTF-8 is standard;
# the others catch older Windows-saved .txt files).
_TXT_ENCODING_FALLBACKS = ("utf-8-sig", "utf-8", "cp1252", "latin-1")


# --------------------------------------------------------------------
# PDF
# --------------------------------------------------------------------

def _extract_pdf_pages(doc: "fitz.Document", source_label: str) -> Tuple[str, Dict[str, Any]]:
    """Shared logic for pulling text out of an already-opened PyMuPDF document."""
    page_texts = []
    per_page_char_counts = []

    for page in doc:
        text = page.get_text("text")  # plain reading-order text
        page_texts.append(text)
        per_page_char_counts.append(len(text))

    num_pages = doc.page_count

    if num_pages == 0:
        raise ExtractionError(f"PDF '{source_label}' has no pages.")

    full_text = "\n".join(page_texts)

    if not full_text.strip():
        # Common with scanned/image-only PDFs (no OCR layer)
        raise ExtractionError(
            f"PDF '{source_label}' produced no extractable text. "
            f"It may be a scanned/image-only document requiring OCR."
        )

    metadata = {
        "file_type": "pdf",
        "num_pages": num_pages,
        "per_page_char_counts": per_page_char_counts,
    }
    return full_text, metadata


def extract_text_from_pdf(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Extract all text from a PDF file on disk, page by page (works for
    any number of pages -- large multi-page documents are supported)."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"PDF not found: {file_path}")

    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise ExtractionError(f"Could not open PDF '{file_path}': {e}") from e

    try:
        if doc.is_encrypted and not doc.authenticate(""):
            raise ExtractionError(
                f"PDF '{file_path}' is password-protected and could not be opened."
            )
        return _extract_pdf_pages(doc, file_path)
    finally:
        doc.close()


def extract_text_from_pdf_bytes(file_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
    """Extract all text from PDF bytes already in memory (e.g. straight
    from a FastAPI UploadFile) -- no temp file needed."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ExtractionError(f"Could not open in-memory PDF: {e}") from e

    try:
        if doc.is_encrypted and not doc.authenticate(""):
            raise ExtractionError("In-memory PDF is password-protected and could not be opened.")
        return _extract_pdf_pages(doc, "<in-memory PDF>")
    finally:
        doc.close()


# --------------------------------------------------------------------
# DOCX
# --------------------------------------------------------------------

def _extract_docx_content(document: "docx.Document", source_label: str) -> Tuple[str, Dict[str, Any]]:
    """Shared logic for pulling text out of an already-opened python-docx Document."""
    text_chunks = []

    for para in document.paragraphs:
        if para.text.strip():
            text_chunks.append(para.text)

    num_tables = len(document.tables)
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    text_chunks.append(cell.text)

    full_text = "\n".join(text_chunks)

    if not full_text.strip():
        raise ExtractionError(f"DOCX '{source_label}' has no extractable text.")

    metadata = {
        "file_type": "docx",
        "num_paragraphs": len(document.paragraphs),
        "num_tables": num_tables,
    }
    return full_text, metadata


def extract_text_from_docx(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Extract all text from a DOCX file on disk: paragraphs + table
    cell text, in document order. Works for documents of any length."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"DOCX not found: {file_path}")

    try:
        document = docx.Document(file_path)
    except Exception as e:
        raise ExtractionError(f"Could not open DOCX '{file_path}': {e}") from e

    return _extract_docx_content(document, file_path)


def extract_text_from_docx_bytes(file_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
    """Extract all text from DOCX bytes already in memory -- no temp file needed."""
    try:
        document = docx.Document(io.BytesIO(file_bytes))
    except Exception as e:
        raise ExtractionError(f"Could not open in-memory DOCX: {e}") from e

    return _extract_docx_content(document, "<in-memory DOCX>")


# --------------------------------------------------------------------
# TXT
# --------------------------------------------------------------------

def _decode_txt_bytes(file_bytes: bytes, source_label: str) -> Tuple[str, Dict[str, Any]]:
    """
    Decode raw text-file bytes, trying a sequence of encodings (most
    student submissions are UTF-8, but older Windows-saved .txt files
    are sometimes cp1252/latin-1).
    """
    text: Optional[str] = None
    used_encoding: Optional[str] = None

    # Only attempt utf-8-sig first if a BOM is actually present -- otherwise
    # utf-8-sig silently "succeeds" on plain UTF-8 too, which would mask
    # the real encoding in the metadata.
    encodings_to_try = list(_TXT_ENCODING_FALLBACKS)
    if not file_bytes.startswith(b"\xef\xbb\xbf"):
        encodings_to_try = [e for e in encodings_to_try if e != "utf-8-sig"]

    for encoding in encodings_to_try:
        try:
            text = file_bytes.decode(encoding)
            used_encoding = encoding
            break
        except (UnicodeDecodeError, LookupError):
            continue

    if text is None:
        raise ExtractionError(
            f"Could not decode TXT '{source_label}' using any of the supported "
            f"encodings ({', '.join(_TXT_ENCODING_FALLBACKS)})."
        )

    if not text.strip():
        raise ExtractionError(f"TXT '{source_label}' is empty.")

    metadata = {
        "file_type": "txt",
        "encoding_used": used_encoding,
        "num_lines": text.count("\n") + 1,
    }
    return text, metadata


def extract_text_from_txt(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Extract text from a .txt file on disk."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"TXT not found: {file_path}")

    with open(file_path, "rb") as f:
        raw_bytes = f.read()

    return _decode_txt_bytes(raw_bytes, file_path)


def extract_text_from_txt_bytes(file_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
    """Extract text from .txt bytes already in memory."""
    return _decode_txt_bytes(file_bytes, "<in-memory TXT>")


# --------------------------------------------------------------------
# Dispatcher
# --------------------------------------------------------------------

def extract_text(
    source: Union[str, bytes],
    filename: Optional[str] = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    Dispatch to the correct extractor based on file extension.

    This is the single entry point the rest of the pipeline (and
    teammates) should call -- they don't need to know which library
    handles which format.

    Args:
        source: EITHER a file path (str) pointing to a .pdf/.docx/.txt
            on disk, OR raw file bytes (e.g. from a FastAPI
            UploadFile.read()).
        filename: required when `source` is bytes -- used to determine
            the file type from its extension (e.g. "essay.pdf"). Ignored
            when `source` is already a path.

    Raises:
        UnsupportedFileTypeError: extension isn't .pdf, .docx, or .txt
        ValueError: bytes were passed without a filename
    """
    if isinstance(source, (bytes, bytearray)):
        if not filename:
            raise ValueError(
                "filename is required when passing raw bytes, so the file "
                "type can be determined (e.g. filename='essay.pdf')."
            )
        validate_filename(filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext == ".pdf":
            return extract_text_from_pdf_bytes(bytes(source))
        elif ext == ".docx":
            return extract_text_from_docx_bytes(bytes(source))
        elif ext == ".txt":
            return extract_text_from_txt_bytes(bytes(source))

    # Otherwise, treat `source` as a file path
    validate_filename(source)
    ext = os.path.splitext(source)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(source)
    elif ext == ".docx":
        return extract_text_from_docx(source)
    elif ext == ".txt":
        return extract_text_from_txt(source)
