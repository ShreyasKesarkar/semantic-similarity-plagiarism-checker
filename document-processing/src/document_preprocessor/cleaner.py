"""
cleaner.py
----------
Normalizes raw extracted text AND separates document structure
(titles, headings) from actual content sentences.

Changes made based on SBERT teammate feedback:
    1. Repeated headers/footers removed             (was partial, now robust)
    2. Document title detected and separated        (NEW)
    3. Section headings detected and separated      (NEW)
    4. Table header lines removed                   (NEW)
    5. Headings no longer merge into first sentence (NEW - newline inserted)
    6. Standalone leading numbers stripped          (NEW - "1 Researchers..." → "Researchers...")
    7. Pattern-based noise removal                  (NEW - Page N, Chapter N, Figure N, Table N)
"""

from __future__ import annotations

import re
import unicodedata
from typing import List, Tuple, Dict, Any


# ---------------------------------------------------------------------------
# Compiled regex patterns
# ---------------------------------------------------------------------------

# Hyphenation across line breaks:  "exam-\nple" → "example"
_HYPHEN_LINEBREAK_RE = re.compile(r"(\w)-\n(\w)")

# Standalone page number lines: "12", "Page 12", "Page 12 of 30", "- 12 -"
_PAGE_NUMBER_RE = re.compile(
    r"^\s*(page\s+)?-?\s*\d+\s*(of\s+\d+)?\s*-?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Noise patterns the SBERT teammate specifically flagged:
#   "Chapter 3", "Figure 1", "Table 2", "Section 1.2", "Appendix A"
_STRUCTURAL_LABEL_RE = re.compile(
    r"^\s*(chapter|figure|table|section|appendix|exhibit)\s+[\dA-Z][\w.]*\s*[:\-]?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Leading standalone number at the start of a sentence:
#   "1 Researchers have observed..." → "Researchers have observed..."
# Covers "1 ", "1. ", "1) "
_LEADING_NUMBER_RE = re.compile(r"^\d+[\.\)]\s+|^\d+\s+(?=[A-Z])")

# Multiple blank lines / excess whitespace
_MULTI_NEWLINE_RE = re.compile(r"\n{2,}")
_MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")

# Control characters (except \n and \t)
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Bracket citations: "[12]", "[3, 4]"
_BRACKET_CITATION_RE = re.compile(r"\[\d+(,\s*\d+)*\]")


# ---------------------------------------------------------------------------
# Heading / title detection
# ---------------------------------------------------------------------------

def _is_heading(line: str) -> bool:
    """
    Detect whether a line is a heading/title rather than a content sentence.

    A line is treated as a heading if ALL of these hold:
        - It is short (≤ 10 words) — real academic sentences are longer
        - It does NOT end with sentence-ending punctuation (. ? !)
        - It has at least 2 characters

    The word limit is kept conservatively at 10 so that long sentences
    extracted from PDFs (which often lack line breaks) are never
    accidentally classified as headings.
    """
    stripped = line.strip()
    if not stripped:
        return False
    if len(stripped) < 2:
        return False
    word_count = len(stripped.split())
    # Conservative limit — real sentences in academic documents are typically
    # longer than 10 words. Short fragments of 1-10 words without a period
    # are almost always headings, labels, or noise.
    if word_count > 10:
        return False
    if stripped[-1] in ".?!:":
        return False
    return True


def _is_table_header(line: str) -> bool:
    """
    Detect table header lines like "Factor    Effect on Ecosystem".

    Heuristic: a short line (≤ 10 words) containing 2+ consecutive
    spaces (tab-separated columns) that doesn't end with punctuation.
    """
    stripped = line.strip()
    if not stripped:
        return False
    if len(stripped.split()) > 10:
        return False
    if stripped[-1] in ".?!":
        return False
    # Multiple spaces suggest column alignment (tab-stop formatting)
    if re.search(r" {2,}", stripped):
        return True
    return False


# ---------------------------------------------------------------------------
# Header / footer removal (frequency-based)
# ---------------------------------------------------------------------------

def remove_headers_footers(text: str, min_repeats: int = 2) -> str:
    """
    Remove repeated headers/footers.

    Changed min_repeats default from 3 → 2 based on SBERT feedback:
    "Department of Environmental Science" appeared on every page but
    on shorter documents (2-3 pages) it only repeated twice before,
    which was below the old threshold of 3 and wasn't being removed.
    """
    lines = text.split("\n")
    short_lines = [ln.strip() for ln in lines if 0 < len(ln.strip()) <= 80]

    counts: Dict[str, int] = {}
    for ln in short_lines:
        counts[ln] = counts.get(ln, 0) + 1

    repeated = {ln for ln, c in counts.items() if c >= min_repeats}
    if not repeated:
        return text

    cleaned = [ln for ln in lines if ln.strip() not in repeated]
    return "\n".join(cleaned)


# ---------------------------------------------------------------------------
# Main cleaning entry point
# ---------------------------------------------------------------------------

def clean_and_extract_structure(
    text: str,
    strip_citations: bool = False,
    strip_headers_footers: bool = True,
    header_footer_min_repeats: int = 2,
) -> Tuple[str, Dict[str, Any]]:
    """
    Clean raw extracted text AND extract document structure metadata.

    This is the upgraded entry point (replacing the old clean_text()).
    It does two things in one pass:
        1. Returns cleaned prose text (ready for sentence segmentation)
        2. Returns a structure dict containing detected title + headings
           so the pipeline can store them as metadata instead of passing
           them to SBERT as fake "sentences"

    Returns:
        (cleaned_text, structure) where structure = {
            "title": "The Impact of Climate Change...",  # or None
            "headings": ["Introduction", "3.1 Related Work", ...]
        }
    """
    if not text:
        return "", {"title": None, "headings": []}

    # --- Step 1: unicode normalization ---
    text = unicodedata.normalize("NFKC", text)

    # --- Step 2: fix PDF line-break hyphenation ---
    text = _HYPHEN_LINEBREAK_RE.sub(r"\1\2", text)

    # --- Step 3: remove page numbers ---
    text = _PAGE_NUMBER_RE.sub("", text)

    # --- Step 4: remove structural labels (Chapter N, Figure N, etc.) ---
    text = _STRUCTURAL_LABEL_RE.sub("", text)

    # --- Step 5: remove repeated headers/footers ---
    if strip_headers_footers:
        text = remove_headers_footers(text, min_repeats=header_footer_min_repeats)

    # --- Step 6: control characters ---
    text = _CONTROL_CHAR_RE.sub("", text)

    # --- Step 7: citations ---
    if strip_citations:
        text = _BRACKET_CITATION_RE.sub("", text)

    # --- Step 8: whitespace normalisation ---
    text = _MULTI_SPACE_RE.sub(" ", text)
    text = _MULTI_NEWLINE_RE.sub("\n", text)

    # --- Step 9: line-by-line pass ---
    # Detect headings and table headers, remove them from the prose
    # text but collect them as metadata. Also insert a newline after
    # each heading so it doesn't merge with the following sentence
    # (the SBERT teammate's bug: "Department of CS Scientists have...").
    lines = text.split("\n")
    title: str | None = None
    headings: List[str] = []
    prose_lines: List[str] = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        if _is_table_header(stripped):
            # Drop table headers entirely (don't even keep as metadata —
            # "Factor   Effect on Ecosystem" has no semantic value)
            continue

        if _is_heading(stripped):
            if title is None:
                # First heading detected = document title
                title = stripped
            else:
                headings.append(stripped)
            # Do NOT add to prose_lines — headings are metadata only.
            # This also prevents them from being merged into the next sentence.
            continue

        # Strip leading standalone numbers from real sentences:
        # "1 Researchers have observed..." → "Researchers have observed..."
        stripped = _LEADING_NUMBER_RE.sub("", stripped)

        if stripped:
            prose_lines.append(stripped)

    cleaned_text = "\n".join(prose_lines).strip()
    structure = {"title": title, "headings": headings}

    return cleaned_text, structure


def clean_text(
    text: str,
    strip_citations: bool = False,
    strip_headers_footers: bool = True,
    header_footer_min_repeats: int = 2,
) -> str:
    """
    Legacy entry point — returns cleaned text only (no structure metadata).
    Kept for backwards compatibility with tests that call clean_text() directly.
    """
    cleaned, _ = clean_and_extract_structure(
        text,
        strip_citations=strip_citations,
        strip_headers_footers=strip_headers_footers,
        header_footer_min_repeats=header_footer_min_repeats,
    )
    return cleaned
