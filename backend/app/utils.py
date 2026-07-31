from __future__ import annotations

import re
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    text = clean_text(text)
    if not text:
        return []

    try:
        import nltk

        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            try:
                nltk.download("punkt", quiet=True)
            except Exception:
                pass
        tokenizer = nltk.tokenize.sent_tokenize
        sentences = [sentence.strip() for sentence in tokenizer(text) if sentence.strip()]
        if sentences:
            return sentences
    except Exception:
        pass

    try:
        import spacy

        try:
            nlp = spacy.load("en_core_web_sm")
        except Exception:
            nlp = spacy.blank("en")
            if "sentencizer" not in nlp.pipe_names:
                nlp.add_pipe("sentencizer")
        doc = nlp(text)
        sentences = [sentence.text.strip() for sentence in doc.sents if sentence.text.strip()]
        if sentences:
            return sentences
    except Exception:
        pass

    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def extract_text_from_pdf(path: Path) -> str:
    parts: list[str] = []
    with fitz.open(path) as document:
        for page in document:
            parts.append(page.get_text("text"))
    return clean_text("\n".join(parts))


def extract_text_from_docx(path: Path) -> str:
    document = Document(path)
    parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    return clean_text("\n".join(parts))


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    if suffix == ".docx":
        return extract_text_from_docx(path)
    raise ValueError(f"Unsupported file type: {suffix}")
