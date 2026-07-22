import sys
import os
import pytest
import numpy as np

# Ensure sbert_module src is in the system path for testing
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from sbert_module import (
    get_embeddings,
    get_embedding,
    compare_sentences,
    compare_documents,
    get_risk,
)


def test_embedding_generation():
    """Verify that SBERT generating embeddings works and returns correct dimensions (384 for MiniLM)."""
    texts = ["Climate change impacts marine life.", "Acidification affects corals."]
    embeddings = get_embeddings(texts)
    
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (2, 384)
    
    # Test single embedding
    single_emb = get_embedding(texts[0])
    assert isinstance(single_emb, np.ndarray)
    assert single_emb.shape == (384,)


def test_empty_embedding_generation():
    """Verify empty input returns an empty array with the correct dimensions."""
    embeddings = get_embeddings([])
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (0, 384)


def test_compare_sentences():
    """Verify similarity comparison between two single sentences."""
    s1 = "Carbon emissions are rising globally."
    s2 = "Worldwide greenhouse gas emissions continue to increase."
    s3 = "Cooking pasta requires boiling water."

    score_similar = compare_sentences(s1, s2)
    score_dissimilar = compare_sentences(s1, s3)

    assert isinstance(score_similar, float)
    assert isinstance(score_dissimilar, float)
    assert score_similar > score_dissimilar
    assert 0.0 <= score_similar <= 1.0


def test_compare_documents():
    """Verify that batched comparison works and identifies correct sentence mapping."""
    doc1 = [
        "Deforestation leads to species extinction.",
        "Renewable energy is growing rapidly."
    ]
    doc2 = [
        "Solar and wind power are expanding fast.",
        "Cutting down forests causes loss of biodiversity."
    ]

    result = compare_documents(doc1, doc2)
    
    assert "overall_similarity" in result
    assert "matches" in result
    assert len(result["matches"]) == 2

    # Verify best match pairing logic
    match_1 = result["matches"][0]
    assert match_1["sentence_a"] == doc1[0]
    assert match_1["sentence_b"] == doc2[1] # Should match cutting down forests
    assert match_1["score"] > 0.6

    match_2 = result["matches"][1]
    assert match_2["sentence_a"] == doc1[1]
    assert match_2["sentence_b"] == doc2[0] # Should match solar/wind power
    assert match_2["score"] > 0.6


def test_compare_documents_empty():
    """Verify comparing empty lists handles gracefully."""
    result = compare_documents([], ["Some sentence."])
    assert result["overall_similarity"] == 0.0
    assert result["matches"] == []

    result = compare_documents(["Some sentence."], [])
    assert result["overall_similarity"] == 0.0
    assert result["matches"] == []


def test_risk_assessment():
    """Verify risk categories mapping similarity scores."""
    assert get_risk(15.0) == "Low"
    assert get_risk(30.0) == "Medium"
    assert get_risk(59.9) == "Medium"
    assert get_risk(60.0) == "High"
    assert get_risk(95.5) == "High"
