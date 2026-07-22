"""
sbert_module
============
Sentence-BERT (SBERT) Semantic Similarity module for the AI Plagiarism Detection System.

Scope:
    - Generates vector embeddings for sentences using SBERT (all-MiniLM-L6-v2)
    - Compares sentences using cosine similarity
    - Performs batched comparison of two documents to find sentence-level plagiarism
    - Determines plagiarism risk level (Low, Medium, High) based on similarity scores
"""

from .sbert_service import (
    get_model,
    get_embeddings,
    get_embedding,
)
from .similarity_engine import compare_sentences
from .document_similarity import compare_documents

from .risk_engine import (
    get_risk,
)

__all__ = [
    "get_model",
    "get_embeddings",
    "get_embedding",
    "compare_sentences",
    "compare_documents",
    "get_risk",
]

__version__ = "0.1.0"
