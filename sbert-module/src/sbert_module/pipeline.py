"""
pipeline.py

This module acts as the entry point for the SBERT module.

Input:
    Processed JSON from the Document Processing module.

Output:
    Semantic similarity results.
"""

from .document_similarity import compare_documents
import re

def filter_sentences(sentences, min_words=4):
    """
    Final cleanup before SBERT embedding generation.
    """

    filtered = []

    blocked_prefixes = (
        "page",
        "chapter",
        "table",
        "figure",
        "appendix",
        "references",
        "bibliography",
        "department"
    )

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        # Remove leading numbers (e.g. "1 Researchers...")
        sentence = re.sub(r"^\d+\s*", "", sentence)

        # Ignore very short text
        if len(sentence.split()) < min_words:
            continue

        lower = sentence.lower()

        # Ignore headings
        if lower.startswith(blocked_prefixes):
            continue

        # Ignore sentences without punctuation
        if "." not in sentence and "?" not in sentence and "!" not in sentence:
            continue

        filtered.append(sentence)

    return filtered


def compare_processed_documents(processed_documents):

    doc1_sentences = filter_sentences(
        processed_documents["document_a"]["sentences"]
    )

    doc2_sentences = filter_sentences(
        processed_documents["document_b"]["sentences"]
    )

    # ---------- DEBUG ----------
    print("\nDocument A sentences:")
    for s in doc1_sentences:
        print(repr(s))

    print("\nDocument B sentences:")
    for s in doc2_sentences:
        print(repr(s))
    # ---------------------------

    return compare_documents(doc1_sentences, doc2_sentences)