from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app
from app.models import MatchedSentencePair, RiskLevel, SimilarityResult


client = TestClient(app)


class FakeService:
    def compare_files(self, document_a, document_b):
        return SimilarityResult(
            id="abc123",
            document_a_name=document_a.name,
            document_b_name=document_b.name,
            overall_similarity_percent=87.0,
            risk_level=RiskLevel.high,
            matched_sections=[
                MatchedSentencePair(
                    sentence_index_a=1,
                    sentence_index_b=2,
                    text_a="Alpha.",
                    text_b="Beta.",
                    similarity_percent=94.0,
                )
            ],
            recommendation="Manual review recommended.",
            checked_at=datetime.now(timezone.utc).isoformat(),
        )


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_compare_returns_frontend_shape(monkeypatch):
    from app import main as backend_main

    backend_main.service = FakeService()

    files = {
        "document_a": ("a.pdf", BytesIO(b"fake pdf content"), "application/pdf"),
        "document_b": ("b.docx", BytesIO(b"fake docx content"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    }

    response = client.post("/compare", files=files)
    assert response.status_code == 200

    body = response.json()
    assert body["document_a_name"] == "a.pdf"
    assert body["document_b_name"] == "b.docx"
    assert body["overall_similarity_percent"] == 87.0
    assert body["risk_level"] == "high"
    assert len(body["matched_sections"]) == 1
