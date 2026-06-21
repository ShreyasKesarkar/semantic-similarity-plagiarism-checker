"""
cli.py
------
Standalone command-line interface for the document preprocessing
module. Useful for testing/demoing your part independently before
it's wired into the FastAPI backend.

Usage:
    # Process a single document, print JSON to stdout
    python -m document_preprocessor.cli essay.pdf

    # Process a single document, save JSON to a file
    python -m document_preprocessor.cli essay.pdf -o essay_output.json

    # Process a pair of documents (Document A vs Document B use case)
    python -m document_preprocessor.cli essay_a.pdf essay_b.docx -o pair_output.json

    # .txt files work too
    python -m document_preprocessor.cli essay_a.txt essay_b.txt -o pair_output.json
"""

from __future__ import annotations

import argparse
import json
import sys

from .pipeline import process_document, process_document_pair


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract, clean, and sentence-segment academic documents "
        "(PDF/DOCX/TXT) for the plagiarism detection pipeline."
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Path(s) to input file(s). Provide one file for single-document "
        "mode, or two files for Document A vs Document B mode. "
        "Supported types: .pdf, .docx, .txt",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to write JSON output. If omitted, prints to stdout.",
    )
    parser.add_argument(
        "--strip-citations",
        action="store_true",
        help="Remove bracket-style citations like [12] before segmentation.",
    )
    parser.add_argument(
        "--min-sentence-words",
        type=int,
        default=4,
        help="Drop sentences with fewer than this many words (default: 4).",
    )
    parser.add_argument(
        "--max-size-mb",
        type=float,
        default=None,
        help="Optional max file size in MB (default: no limit).",
    )

    args = parser.parse_args()

    if len(args.files) > 2:
        parser.error("Provide at most 2 files (single document, or Document A + B).")

    kwargs = dict(
        strip_citations=args.strip_citations,
        min_sentence_words=args.min_sentence_words,
        max_size_mb=args.max_size_mb,
    )

    try:
        if len(args.files) == 2:
            result = process_document_pair(args.files[0], args.files[1], **kwargs)
        else:
            result = process_document(args.files[0], **kwargs)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    json_str = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"Output written to {args.output}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
