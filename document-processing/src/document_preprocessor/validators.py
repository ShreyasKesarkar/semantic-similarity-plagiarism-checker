"""
validators.py
--------------
Input validation for the document preprocessing module.

Per project requirements:
    1. The module receives 2 files (a pair: Document A + Document B)
    2. Only PDF, DOCX, and TXT files are accepted -- anything else
       must be rejected with a clear error
    3. Documents can be any size / any number of pages -- no hard
       size limit is enforced by default (an optional cap is provided
       for production hardening, but it's off unless explicitly set)

This module is intentionally usable two ways:
    - Internally, by extractor.py / pipeline.py before doing any
      extraction work (fail fast, don't waste time parsing a file
      we're going to reject anyway).
    - Externally, by the UI/backend team -- e.g. the backend dev can
      call `is_supported_filename()` right after receiving an upload,
      before even calling into this module, to return a fast 400
      error to the Flutter UI.
"""

from __future__ import annotations

import os
from typing import Optional, Union

from .exceptions import UnsupportedFileTypeError, ValidationError

# Single source of truth for which file types this module accepts.
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def get_extension(filename: str) -> str:
    """Return the lowercase extension of a filename/path, e.g. '.pdf'."""
    return os.path.splitext(filename)[1].lower()


def is_supported_filename(filename: str) -> bool:
    """
    Quick boolean check -- does this filename look like a type we support?
    Does NOT open or read the file. Handy for the UI/backend team to use
    as a fast pre-check before even uploading/sending the file to us.
    """
    return get_extension(filename) in SUPPORTED_EXTENSIONS


def validate_filename(filename: str) -> None:
    """
    Raise UnsupportedFileTypeError if the filename's extension isn't
    one of SUPPORTED_EXTENSIONS. Called internally by extract_text()
    before any parsing is attempted.
    """
    ext = get_extension(filename)
    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{ext or '(none)'}'. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )


def validate_not_empty(source: Union[str, bytes]) -> None:
    """
    Raise ValidationError if the input is a 0-byte file. This is a
    cheap sanity check that runs before extraction; extractor.py also
    independently catches the case where a file has *some* bytes but
    no usable text (e.g. a blank PDF page).
    """
    if isinstance(source, (bytes, bytearray)):
        if len(source) == 0:
            raise ValidationError("Uploaded file is empty (0 bytes).")
    else:
        if os.path.isfile(source) and os.path.getsize(source) == 0:
            raise ValidationError(f"File '{source}' is empty (0 bytes).")


def validate_max_size(size_bytes: int, max_size_mb: Optional[float] = None) -> None:
    """
    Optional size guard.

    Per project requirements, documents "can be any size" -- so this is
    OFF by default (max_size_mb=None means no limit is enforced). If
    your team later wants to protect the server from abuse (e.g. a
    500MB upload), pass max_size_mb to enable a cap:

        validate_max_size(len(file_bytes), max_size_mb=200)
    """
    if max_size_mb is None:
        return
    max_bytes = max_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise ValidationError(
            f"File size {size_bytes / (1024 * 1024):.1f}MB exceeds the "
            f"{max_size_mb}MB limit."
        )
