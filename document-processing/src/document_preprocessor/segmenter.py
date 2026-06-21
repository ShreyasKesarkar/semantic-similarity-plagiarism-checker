"""
segmenter.py
------------
Splits cleaned text into sentences using NLTK's Punkt tokenizer.

This is the final preprocessing step before sentences get handed off
to the SBERT embedding stage, so the output here should be a clean
list of individual, analysis-ready sentences.
"""

from __future__ import annotations

from typing import List

import nltk

_PUNKT_READY = False


def _ensure_punkt() -> None:
    """
    Make sure NLTK's sentence tokenizer data is available, downloading
    it on first use if necessary. Cached after the first successful
    check so we don't hit the filesystem/network on every call.
    """
    global _PUNKT_READY
    if _PUNKT_READY:
        return

    for resource in ("tokenizers/punkt_tab", "tokenizers/punkt"):
        try:
            nltk.data.find(resource)
            _PUNKT_READY = True
            return
        except LookupError:
            continue

    # Not found locally -- try to download (requires network access).
    try:
        nltk.download("punkt_tab", quiet=True)
        _PUNKT_READY = True
    except Exception as e:
        raise RuntimeError(
            "NLTK 'punkt_tab' tokenizer data is not available and could "
            "not be downloaded automatically. Run "
            "`python -m nltk.downloader punkt_tab` once on this machine."
        ) from e


def segment_sentences(
    text: str,
    min_words: int = 4,
) -> List[str]:
    """
    Split cleaned text into sentences and filter out low-value fragments.

    Args:
        text: cleaned text (output of cleaner.clean_text)
        min_words: sentences with fewer words than this are dropped.
            Filters out junk like stray list bullets, lone numbers, or
            section labels ("3.2", "Figure 1.") that aren't real
            sentences and would just add noise to SBERT comparison.

    Returns:
        List of sentence strings, in original order, whitespace-trimmed.
        Works the same regardless of document length -- a 500-page
        document just produces a longer list.
    """
    if not text or not text.strip():
        return []

    _ensure_punkt()

    raw_sentences = nltk.sent_tokenize(text)

    sentences = []
    for s in raw_sentences:
        s = s.strip().replace("\n", " ")
        s = " ".join(s.split())  # collapse any leftover internal whitespace
        if not s:
            continue
        if len(s.split()) < min_words:
            continue
        sentences.append(s)

    return sentences
