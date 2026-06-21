# document-preprocessor

**Document Processing module** for the AI-Powered Plagiarism Detection
System — built for teachers to compare two students' assignments/answer
sheets/academic documents and generate a plagiarism report.

This module owns the first half of the pipeline:

```
Document A + Document B
        ↓
  Validate file type        <-- this module
        ↓
  Text Extraction            <-- this module
        ↓
  Text Cleaning               <-- this module
        ↓
 Sentence Segmentation        <-- this module
        ↓
  SBERT Embeddings             (other team member)
        ↓
 Cosine Similarity             (other team member)
        ↓
  Risk Assessment               (other team member)
        ↓
 Plagiarism Report              (other team member)
```

It takes two documents in (PDF, DOCX, or TXT, in any combination), and
hands back clean, structured, sentence-level output that the SBERT
similarity engine can consume directly.

---

## Repo structure

This is meant to live as its own folder inside the team's monorepo,
alongside the SBERT module, the FastAPI backend, and the Flutter UI:

```
document-processing/
├── src/
│   └── document_preprocessor/
│       ├── __init__.py        # public API — what teammates import
│       ├── exceptions.py       # shared exception types
│       ├── validators.py       # file type + size validation
│       ├── extractor.py        # PDF/DOCX/TXT → raw text
│       ├── cleaner.py          # raw text → normalized text
│       ├── segmenter.py        # normalized text → list of sentences
│       ├── pipeline.py         # orchestrates the steps above
│       └── cli.py               # command-line interface
├── tests/
│   ├── fixtures.py             # shared test helpers
│   ├── test_validators.py
│   ├── test_extractor.py
│   ├── test_cleaner.py
│   ├── test_segmenter.py
│   └── test_pipeline.py         # full end-to-end integration tests
├── sample_files/                 # synthetic test documents (safe to delete)
├── scripts/
│   └── setup_nltk.py             # one-time NLTK data download
├── pyproject.toml                 # makes this pip-installable
├── requirements.txt
├── .gitignore
└── README.md
```

A **src-layout** was used (package code under `src/`) since this is going
into a shared monorepo — it keeps the installable package cleanly
separated from tests/scripts/sample data, and avoids accidental imports
of the wrong thing.

## Installation

**As a standalone module (for your own development/testing):**
```bash
pip install -r requirements.txt
python scripts/setup_nltk.py     # one-time download of sentence-tokenizer data
```

**As an installed package (for the backend/SBERT teammate to depend on):**
```bash
pip install -e ./document-processing
```
This uses `pyproject.toml`, so after this, anyone in the monorepo can do
`from document_preprocessor import process_document_pair` regardless of
which folder their code lives in.

## Quick start (Python)

```python
from document_preprocessor import process_document, process_document_pair

# Single document
result = process_document("essay.pdf")
print(result["sentences"])

# The core use case: Document A vs Document B
result = process_document_pair("essay_a.pdf", "essay_b.docx")
result["document_a"]["sentences"]
result["document_b"]["sentences"]
```

## Quick start (command line)

```bash
cd document-processing
python -m document_preprocessor.cli sample_files/sample_document.pdf

python -m document_preprocessor.cli sample_files/sample_document.pdf -o output.json

python -m document_preprocessor.cli essay_a.pdf essay_b.docx -o pair_output.json

# .txt files work too
python -m document_preprocessor.cli essay_a.txt essay_b.txt -o pair_output.json
```

> The CLI is path-based only (it reads files from disk). Bytes-based
> input (below) is for when this module is called directly from code.

---

## Input contract — what to give this module

Per the project requirements, the module:
1. Takes **two files** as input (the Document A / Document B comparison)
2. Accepts **only PDF, DOCX, or TXT** — anything else is rejected with a
   clear `UnsupportedFileTypeError`
3. Places **no limit on document size or page count** by default — a
   500-page thesis is processed the same way as a 1-page essay

It accepts **either** of these input forms, so it doesn't matter how the
UI/backend team chooses to handle uploads:

| Input type | When to use | How |
|---|---|---|
| **File path** (`str`) | File already saved on disk | `process_document("essay.pdf")` |
| **Raw bytes** | File fresh from a web upload, no temp file needed | `process_document(file_bytes, filename="essay.pdf")` |

The `filename` argument is only required in the bytes case — it's how
the module knows whether to treat it as PDF, DOCX, or TXT.

### Pre-checking a filename without uploading (for the UI team)

```python
from document_preprocessor import is_supported_filename

is_supported_filename("essay.pdf")   # True
is_supported_filename("essay.rtf")   # False
```
Useful for the Flutter/backend team to reject obviously-wrong files
client-side before even sending them over.

### Validation errors this module can raise

| Exception | When |
|---|---|
| `UnsupportedFileTypeError` | File isn't `.pdf`, `.docx`, or `.txt` |
| `ValidationError` | File is empty (0 bytes), or exceeds an optional `max_size_mb` cap |
| `ExtractionError` | Right file type, but couldn't be parsed (corrupted, password-protected, scanned/image-only PDF with no text layer) |
| `FileNotFoundError` | A path was given but doesn't exist |

All four are exported from the package (`from document_preprocessor import ValidationError`, etc.) so the FastAPI backend can catch them and return clean HTTP error responses.

## How it fits into FastAPI

This is the version I'd hand to the backend teammate — reads both
uploads straight into memory, never touches disk:

```python
from fastapi import FastAPI, UploadFile, HTTPException
from document_preprocessor import (
    process_document_pair,
    UnsupportedFileTypeError,
    ValidationError,
    ExtractionError,
)

app = FastAPI()

@app.post("/preprocess")
async def preprocess(file_a: UploadFile, file_b: UploadFile):
    bytes_a = await file_a.read()
    bytes_b = await file_b.read()

    try:
        result = process_document_pair(
            bytes_a, bytes_b,
            filename_a=file_a.filename,
            filename_b=file_b.filename,
        )
    except (UnsupportedFileTypeError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ExtractionError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return result   # -> handed straight to the SBERT teammate's endpoint
```

## Output contract — what this module hands the SBERT team

```jsonc
{
  "document_a": {
    "document_id": "Document A",
    "source_path": "/full/path/essay_a.pdf",  // null if bytes were passed in
    "file_type": "pdf",
    "extraction_metadata": {
      "file_type": "pdf",
      "num_pages": 5,
      "per_page_char_counts": [482, 253, "..."]
    },
    "raw_char_count": 736,
    "cleaned_char_count": 732,
    "sentence_count": 6,
    "sentences": [
      "Global warming is dramatically changing marine ecosystems worldwide.",
      "Increasing sea temperatures have caused extensive coral bleaching..."
    ],
    "processed_at": "2026-06-21T13:07:08.031388+00:00"
  },
  "document_b": { "...": "same shape" }
}
```

**For the SBERT teammate:** the `sentences` array is the only field you
need — pass it straight into `model.encode(sentences)`. Each sentence's
position in that array is its implicit ID, so the risk-assessment/report
step can say "sentence 5 in Document A" by just using the list index.

`extraction_metadata` differs slightly by file type:
- **PDF:** `num_pages`, `per_page_char_counts`
- **DOCX:** `num_paragraphs`, `num_tables`
- **TXT:** `encoding_used`, `num_lines`

## What the cleaning step actually does

- Fixes words broken across line breaks by PDF extraction (`exam-\nple` → `example`)
- Removes standalone page-number lines (`12`, `Page 3 of 10`)
- Removes repeated headers/footers — a line is treated as one if it's
  short (≤80 chars) and repeats at least `header_footer_min_repeats`
  times (default: 3, configurable)
- Normalizes unicode (smart quotes, ligatures like "ﬁ" → "fi")
- Collapses excess whitespace
- Optionally strips bracket-style citations like `[12]` (off by default
  — pass `strip_citations=True` if your team wants this)

## What the segmentation step does

- Splits cleaned text into sentences using NLTK's Punkt tokenizer
- Drops very short fragments (default: fewer than 4 words) like stray
  figure labels (`"Figure 1."`) that would just add noise to SBERT
  comparison

## Known limitations

- **Scanned/image-only PDFs** aren't supported — no OCR step. Raises a
  clear `ExtractionError` instead of silently returning nothing.
- **Header/footer detection is frequency-based**, so on very short
  documents (1–2 pages) a real header may not repeat enough times to be
  caught. Lower `header_footer_min_repeats` for short sample docs.
- **Inline footnote markers without brackets** (e.g. a bare superscript
  `1`) aren't stripped — only bracket-style citations like `[12]` are
  currently handled.
- For **very large file uploads** (e.g. >100MB) handed in as bytes, the
  backend may prefer saving to a temp file rather than holding the full
  upload in memory — that's a backend-side decision; this module
  supports either approach.

## Testing

```bash
python -m pytest tests/ -v
```

60 tests across 5 files, covering: file-type/size validation, PDF/DOCX/TXT
extraction (path-based and bytes-based), text cleaning (whitespace,
hyphenation, page numbers, headers/footers, citations), sentence
segmentation, the full end-to-end pipeline for all 3 file types, the
Document A/B pair flow (including mixed file types and mixed path/bytes
input), and large-document handling (40-page PDF, 300-paragraph DOCX).

## Sample files

`sample_files/` contains synthetic PDF/DOCX/TXT documents (with
deliberately paraphrased overlapping content) used to validate the
pipeline and demo the system. Try:

```bash
python -m document_preprocessor.cli sample_files/sample_document.pdf sample_files/sample_document.docx
```
