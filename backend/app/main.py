from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

from .models import SimilarityResult
from .services import DocumentSimilarityService
from .utils import SUPPORTED_EXTENSIONS


app = FastAPI(
    title="Semantic Similarity Plagiarism Checker API",
    description="Backend for academic plagiarism detection using semantic similarity.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = DocumentSimilarityService()


@app.on_event("startup")
async def warm_up_model() -> None:
    await run_in_threadpool(service.warm_up)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


async def _save_upload(upload: UploadFile, directory: Path) -> Path:
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    target = directory / (upload.filename or f"upload{suffix}")
    content = await upload.read()
    target.write_bytes(content)
    return target


@app.post("/compare", response_model=SimilarityResult)
async def compare_documents(
    document_a: UploadFile = File(...),
    document_b: UploadFile = File(...),
) -> SimilarityResult:
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir)
        saved_a = await _save_upload(document_a, temp_path)
        saved_b = await _save_upload(document_b, temp_path)

        try:
            return await run_in_threadpool(service.compare_files, saved_a, saved_b)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error)) from error
