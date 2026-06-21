"""
exceptions.py
-------------
Shared exception types for the document preprocessing module.

Centralized here (rather than defined inside extractor.py or
validators.py) so both modules can raise/catch the same types without
circular imports.
"""


class UnsupportedFileTypeError(Exception):
    """Raised when a file's extension isn't one we know how to parse.

    Supported types: .pdf, .docx, .txt
    """
    pass


class ExtractionError(Exception):
    """Raised when a file is the right type but fails to open/parse
    (corrupted, password-protected, empty, undecodable, etc.)."""
    pass


class ValidationError(Exception):
    """Raised when input validation fails before extraction is even
    attempted (e.g. a 0-byte file, or a file over an optional size cap)."""
    pass
