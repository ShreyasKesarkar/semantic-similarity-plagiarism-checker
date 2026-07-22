# SBERT Semantic Similarity Module

This is the **Sentence-BERT (SBERT) Semantic Similarity module** for the AI-Powered Plagiarism Checker. It handles embedding generation, vectorized sentence-level comparison, and plagiarism risk assessment.

```
                  Document Preprocessor Output
                                ↓
                      [SBERT Embeddings]
                Converts sentences into 384-d vectors
                                ↓
                     [Cosine Similarity]
               Vectorized matrix multiplication
                                ↓
                     [Risk Assessment Engine]
               Plagiarism Risk Level (Low/Med/High)
```

This module consumes the cleaned, structured sentence lists produced by the `document-preprocessor` module and runs similarity comparisons.

---

## Performance Optimization

To compare two documents with $N$ and $M$ sentences, comparing them sentence-by-sentence in a nested loop would require $2 \times N \times M$ invocations of the SBERT model, which is extremely slow.

This module resolves this via **batching & vectorization**:
1. Encode all sentences in Document A in a single SBERT forward pass.
2. Encode all sentences in Document B in a single SBERT forward pass.
3. Compute the full pairwise cosine similarity matrix in a single step using scikit-learn.
4. Extract the best matching sentences using NumPy indexing.

This reduces SBERT model calls from $O(N \times M)$ to **exactly 2 calls**, improving execution speeds by multiple orders of magnitude.

---

## Directory Structure

```
sbert-module/
├── src/
│   └── sbert_module/
│       ├── __init__.py        # Public API
│       ├── sbert_service.py   # Model loader & embedding generator
│       ├── similarity_engine.py # Optimized similarity calculations
│       ├── risk_engine.py     # Risk classification thresholds
│       └── main.py            # Integration CLI run script
├── tests/
│   └── test_similarity.py     # Unit and integration tests
├── pyproject.toml             # Package configuration (setuptools)
├── requirements.txt           # Pip dependencies list
├── .gitignore                 # Ignores model cache and bytecodes
└── README.md                  # This file
```

---

## Setup & Installation

### Dependencies
This module requires the following packages:
- `sentence-transformers`
- `scikit-learn`
- `numpy`
- `torch`

To install dependencies locally:
```bash
pip install -r requirements.txt
```

To install the SBERT module itself in editable mode:
```bash
pip install -e ./sbert-module
```

---

## Quick Start (Python API)

Ensure both `document-preprocessor` and `sbert-module` are installed or added to your Python path:

```python
from document_preprocessor import process_document_pair
from sbert_module import compare_documents, get_risk

# 1. Preprocess documents
prep = process_document_pair("essay_a.pdf", "essay_b.docx")
sentences_a = prep["document_a"]["sentences"]
sentences_b = prep["document_b"]["sentences"]

# 2. Compare using SBERT
analysis = compare_documents(sentences_a, sentences_b)

# 3. Assess Plagiarism Risk
similarity = analysis["overall_similarity"]
risk = get_risk(similarity)

print(f"Similarity: {similarity:.2f}% (Risk: {risk})")
```
