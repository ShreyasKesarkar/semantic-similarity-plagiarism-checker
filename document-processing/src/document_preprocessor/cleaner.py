"""
cleaner.py
----------
Normalizes raw extracted text before sentence segmentation.

Why this matters for plagiarism detection:
    SBERT embeddings are sensitive to noisy input. Leftover artifacts
    from PDF/DOCX/TXT extraction -- broken hyphenation, repeated headers/
    footers, stray page numbers, weird whitespace -- can split or
    corrupt sentences, which directly hurts similarity scoring
    downstream. This module's job is to make the text look like clean
    prose again before it gets segmented into sentences.
"""

from __future__ import annotations

import re
import unicodedata


# --- Regex patterns (compiled once, reused) ---------------------------

# "exam-\nple" -> "example"  (hyphenation at line breaks, common in PDFs)
_HYPHEN_LINEBREAK_RE = re.compile(r"(\w)-\n(\w)")

# Standalone page-number lines, e.g. "12", "Page 12", "Page 12 of 30", "- 12 -"
_PAGE_NUMBER_RE = re.compile(
    r"^\s*(page\s+)?-?\s*\d+\s*(of\s+\d+)?\s*-?\s*$", re.IGNORECASE | re.MULTILINE
)

# Multiple blank lines / excess whitespace
_MULTI_NEWLINE_RE = re.compile(r"\n{2,}")
_MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")

# Control characters (except newline/tab) that sometimes sneak in
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Common inline citation markers, e.g. "[12]", "[3, 4]" -- OFF by default,
# see strip_citations flag in clean_text().
_BRACKET_CITATION_RE = re.compile(r"\[\d+(,\s*\d+)*\]")


def _fix_hyphenation(text: str) -> str:
    """Rejoin words that were split across a line break with a hyphen."""
    return _HYPHEN_LINEBREAK_RE.sub(r"\1\2", text)


def _remove_page_numbers(text: str) -> str:
    return _PAGE_NUMBER_RE.sub("", text)


def _normalize_unicode(text: str) -> str:
    """
    Normalize unicode (e.g. smart quotes, ligatures) to a consistent
    form. NFKC also collapses some weird PDF font-encoding artifacts
    like 'ﬁ' (fi ligature) into plain 'fi'.
    """
    return unicodedata.normalize("NFKC", text)


def _collapse_whitespace(text: str) -> str:
    text = _MULTI_SPACE_RE.sub(" ", text)
    text = _MULTI_NEWLINE_RE.sub("\n", text)
    return text


def remove_headers_footers(text: str, min_repeats: int = 3) -> str:
    """
    Heuristic removal of repeated headers/footers (e.g. a running
    "Department of Computer Science" line on every page).

    A line is considered a header/footer if it is short (<= 80 chars)
    and appears verbatim 'min_repeats' or more times in the document.
    This is intentionally conservative -- we'd rather miss a header
    than accidentally delete a real, repeated sentence.
    """
    lines = text.split("\n")
    short_lines = [ln.strip() for ln in lines if 0 < len(ln.strip()) <= 80]

    counts: dict[str, int] = {}
    for ln in short_lines:
        counts[ln] = counts.get(ln, 0) + 1

    repeated = {ln for ln, c in counts.items() if c >= min_repeats}

    if not repeated:
        return text

    cleaned_lines = [ln for ln in lines if ln.strip() not in repeated]
    return "\n".join(cleaned_lines)


def clean_text(
    text: str,
    strip_citations: bool = False,
    strip_headers_footers: bool = True,
    header_footer_min_repeats: int = 3,
) -> str:
    """
    Main entry point: run the full cleaning pipeline on raw extracted text.

    Args:
        text: raw text from extractor.py
        strip_citations: if True, removes bracket-style citations like "[12]".
            Off by default since citation removal can be lossy and some
            teams may want citation markers preserved for the report.
        strip_headers_footers: if True, attempts to remove repeated
            header/footer lines (see remove_headers_footers()).
        header_footer_min_repeats: how many times a short line must repeat
            before it's treated as a header/footer. Lower this (e.g. to 2)
            for short documents where a real header may only repeat once
            or twice; raise it if you see real content being stripped.

    Returns:
        Cleaned text, ready for sentence segmentation.
    """
    if not text:
        return ""

    text = _normalize_unicode(text)
    text = _fix_hyphenation(text)
    text = _remove_page_numbers(text)

    if strip_headers_footers:
        text = remove_headers_footers(text, min_repeats=header_footer_min_repeats)

    if strip_citations:
        text = _BRACKET_CITATION_RE.sub("", text)

    text = _CONTROL_CHAR_RE.sub("", text)
    text = _collapse_whitespace(text)

    return text.strip()
