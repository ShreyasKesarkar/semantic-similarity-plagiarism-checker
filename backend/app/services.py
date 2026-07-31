from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from .models import MatchedSentencePair, RiskLevel, SimilarityResult
from .utils import extract_text, split_sentences


def risk_from_percent(percent: float) -> RiskLevel:
    if percent < 30:
        return RiskLevel.low
    if percent < 60:
        return RiskLevel.medium
    return RiskLevel.high


def recommendation_from_risk(risk_level: RiskLevel) -> str:
    if risk_level == RiskLevel.high:
        return (
            "This document contains highly similar content. Manual review of highlighted sections is recommended "
            "before making a final plagiarism determination."
        )
    if risk_level == RiskLevel.medium:
        return (
            "The document shows moderate similarity. Review the matched sections for paraphrasing and proper citations."
        )
    return "The document appears to have low similarity. A brief spot-check is still recommended."


def _clip_percent(value: float) -> float:
    return max(0.0, min(100.0, value))


@dataclass
class SentenceMatch:
    sentence_index_a: int
    sentence_index_b: int
    text_a: str
    text_b: str
    similarity_percent: float


class DocumentSimilarityService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model: SentenceTransformer | None = None

    def warm_up(self) -> None:
        """Load the embedding model once so the first request is faster."""
        self._load_model()

    def _load_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def _embed(self, sentences: list[str]) -> np.ndarray:
        if not sentences:
            return np.zeros((0, 384), dtype=np.float32)

        model = self._load_model()
        embeddings = model.encode(sentences, convert_to_numpy=True, normalize_embeddings=True)
        return np.asarray(embeddings, dtype=np.float32)

    def _match_sentences(
        self,
        sentences_a: list[str],
        embeddings_a: np.ndarray,
        sentences_b: list[str],
        embeddings_b: np.ndarray,
        top_k: int = 3,
    ) -> list[SentenceMatch]:
        if not len(sentences_a) or not len(sentences_b):
            return []

        similarity_matrix = cosine_similarity(embeddings_a, embeddings_b)
        candidates: list[SentenceMatch] = []
        for index_a, row in enumerate(similarity_matrix):
            index_b = int(np.argmax(row))
            score = float(row[index_b]) * 100.0
            candidates.append(
                SentenceMatch(
                    sentence_index_a=index_a + 1,
                    sentence_index_b=index_b + 1,
                    text_a=sentences_a[index_a],
                    text_b=sentences_b[index_b],
                    similarity_percent=_clip_percent(score),
                )
            )

        deduped: dict[tuple[int, int], SentenceMatch] = {}
        for candidate in sorted(candidates, key=lambda item: item.similarity_percent, reverse=True):
            key = (candidate.sentence_index_a, candidate.sentence_index_b)
            deduped.setdefault(key, candidate)

        return list(deduped.values())[:top_k]

    def compare_files(self, document_a: Path, document_b: Path) -> SimilarityResult:
        text_a = extract_text(document_a)
        text_b = extract_text(document_b)

        sentences_a = split_sentences(text_a)
        sentences_b = split_sentences(text_b)

        if not sentences_a or not sentences_b:
            raise ValueError("Both documents must contain extractable text.")

        embeddings_a = self._embed(sentences_a)
        embeddings_b = self._embed(sentences_b)

        similarity_matrix = cosine_similarity(embeddings_a, embeddings_b)
        forward_scores = similarity_matrix.max(axis=1)
        backward_scores = similarity_matrix.max(axis=0)
        overall_similarity = float((forward_scores.mean() + backward_scores.mean()) / 2.0 * 100.0)
        overall_similarity = _clip_percent(overall_similarity)

        matched_sections = self._match_sentences(sentences_a, embeddings_a, sentences_b, embeddings_b)
        risk_level = risk_from_percent(overall_similarity)

        return SimilarityResult(
            id=hashlib.sha1(
                f"{document_a.name}:{document_b.name}:{datetime.now(timezone.utc).isoformat()}".encode("utf-8")
            ).hexdigest()[:12],
            document_a_name=document_a.name,
            document_b_name=document_b.name,
            overall_similarity_percent=overall_similarity,
            risk_level=risk_level,
            matched_sections=[
                MatchedSentencePair(
                    sentence_index_a=match.sentence_index_a,
                    sentence_index_b=match.sentence_index_b,
                    text_a=match.text_a,
                    text_b=match.text_b,
                    similarity_percent=match.similarity_percent,
                )
                for match in matched_sections
            ],
            recommendation=recommendation_from_risk(risk_level),
            checked_at=datetime.now(timezone.utc).isoformat(),
        )
