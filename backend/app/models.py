from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class MatchedSentencePair(BaseModel):
    sentence_index_a: int = Field(..., ge=1)
    sentence_index_b: int = Field(..., ge=1)
    text_a: str
    text_b: str
    similarity_percent: float = Field(..., ge=0, le=100)


class SimilarityResult(BaseModel):
    id: str
    document_a_name: str
    document_b_name: str
    overall_similarity_percent: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    matched_sections: List[MatchedSentencePair]
    recommendation: str
    checked_at: str
