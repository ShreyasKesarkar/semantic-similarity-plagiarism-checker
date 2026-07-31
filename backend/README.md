# FastAPI Backend

This backend powers the semantic similarity plagiarism checker.

## Features
- `POST /compare` accepts two files (`document_a`, `document_b`) as multipart upload.
- Supports `.pdf` and `.docx`.
- Extracts text, cleans it, splits it into sentences, computes embeddings, and calculates cosine similarity.
- Returns a JSON payload that matches the Flutter `SimilarityResultModel` contract.

## Install
```bash
pip install -r requirements.txt
```

## Run
```bash
uvicorn app.main:app --reload
```

## Test
```bash
pytest
```

## Notes
- The service uses `SentenceTransformer('all-MiniLM-L6-v2')` by default.
- If spaCy or NLTK resources are not available, the backend falls back to a regex sentence splitter.