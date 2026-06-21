"""
fixtures.py
-----------
Shared helpers for building throwaway sample PDF/DOCX/TXT files inside
a temp directory during tests, so test files don't depend on anything
outside of themselves.
"""

import docx
import fitz


def make_docx(path, paragraphs):
    d = docx.Document()
    for p in paragraphs:
        d.add_paragraph(p)
    d.save(path)


def make_pdf(path, text, pages=1):
    doc = fitz.open()
    rect = fitz.Rect(50, 50, 545, 780)
    for _ in range(pages):
        page = doc.new_page()
        page.insert_textbox(rect, text, fontsize=11)
    doc.save(path)
    doc.close()


def make_pdf_with_unique_pages(path, texts):
    """
    Like make_pdf, but takes a list of per-page texts instead of
    repeating the same text on every page. Use this for multi-page
    tests where the content should NOT trigger header/footer removal
    (which treats identical repeated short lines as noise -- by
    design, but undesirable when you actually want unique content
    on every page for a realistic large-document test).
    """
    doc = fitz.open()
    rect = fitz.Rect(50, 50, 545, 780)
    for text in texts:
        page = doc.new_page()
        page.insert_textbox(rect, text, fontsize=11)
    doc.save(path)
    doc.close()


def make_empty_pdf(path):
    doc = fitz.open()
    doc.new_page()  # blank page, no text
    doc.save(path)
    doc.close()


def make_txt(path, content, encoding="utf-8"):
    with open(path, "w", encoding=encoding) as f:
        f.write(content)
