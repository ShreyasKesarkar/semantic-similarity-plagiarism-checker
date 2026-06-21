"""
test_extractor.py
------------------
Tests for extractor.py: PDF / DOCX / TXT extraction, both path-based
and bytes-based, plus error handling.
"""

import os
import shutil
import tempfile
import unittest

from document_preprocessor import (
    extract_text,
    extract_text_from_pdf,
    extract_text_from_pdf_bytes,
    extract_text_from_docx,
    extract_text_from_docx_bytes,
    extract_text_from_txt,
    extract_text_from_txt_bytes,
    UnsupportedFileTypeError,
    ExtractionError,
)

from . import fixtures


class TestExtractorBase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)


class TestPdfExtraction(TestExtractorBase):
    def test_extract_pdf_from_path(self):
        path = os.path.join(self.tmpdir, "doc.pdf")
        fixtures.make_pdf(path, "This is a PDF test sentence with enough words.")
        text, meta = extract_text_from_pdf(path)
        self.assertIn("PDF test sentence", text)
        self.assertEqual(meta["file_type"], "pdf")
        self.assertEqual(meta["num_pages"], 1)

    def test_extract_pdf_from_bytes(self):
        path = os.path.join(self.tmpdir, "doc.pdf")
        fixtures.make_pdf(path, "A sentence written to a bytes-based pdf document.")
        with open(path, "rb") as f:
            file_bytes = f.read()
        text, meta = extract_text_from_pdf_bytes(file_bytes)
        self.assertIn("bytes-based pdf", text)
        self.assertEqual(meta["file_type"], "pdf")

    def test_multipage_pdf_extraction(self):
        path = os.path.join(self.tmpdir, "doc.pdf")
        fixtures.make_pdf(path, "Repeated content paragraph for multi-page test.", pages=5)
        text, meta = extract_text_from_pdf(path)
        self.assertEqual(meta["num_pages"], 5)
        self.assertEqual(len(meta["per_page_char_counts"]), 5)

    def test_missing_pdf_raises(self):
        with self.assertRaises(FileNotFoundError):
            extract_text_from_pdf(os.path.join(self.tmpdir, "missing.pdf"))

    def test_empty_pdf_raises_extraction_error(self):
        path = os.path.join(self.tmpdir, "empty.pdf")
        fixtures.make_empty_pdf(path)
        with self.assertRaises(ExtractionError):
            extract_text_from_pdf(path)


class TestDocxExtraction(TestExtractorBase):
    def test_extract_docx_from_path(self):
        path = os.path.join(self.tmpdir, "doc.docx")
        fixtures.make_docx(path, ["First paragraph here.", "Second paragraph here."])
        text, meta = extract_text_from_docx(path)
        self.assertIn("First paragraph", text)
        self.assertEqual(meta["file_type"], "docx")

    def test_extract_docx_from_bytes(self):
        path = os.path.join(self.tmpdir, "doc.docx")
        fixtures.make_docx(path, ["A sentence written to bytes-based docx."])
        with open(path, "rb") as f:
            file_bytes = f.read()
        text, meta = extract_text_from_docx_bytes(file_bytes)
        self.assertIn("bytes-based docx", text)
        self.assertEqual(meta["file_type"], "docx")

    def test_missing_docx_raises(self):
        with self.assertRaises(FileNotFoundError):
            extract_text_from_docx(os.path.join(self.tmpdir, "missing.docx"))


class TestTxtExtraction(TestExtractorBase):
    def test_extract_txt_from_path(self):
        path = os.path.join(self.tmpdir, "doc.txt")
        fixtures.make_txt(path, "This is a plain text test sentence with enough words.")
        text, meta = extract_text_from_txt(path)
        self.assertIn("plain text test sentence", text)
        self.assertEqual(meta["file_type"], "txt")
        self.assertEqual(meta["encoding_used"], "utf-8")

    def test_extract_txt_from_bytes(self):
        content = "A sentence written to a bytes-based txt document."
        text, meta = extract_text_from_txt_bytes(content.encode("utf-8"))
        self.assertIn("bytes-based txt", text)
        self.assertEqual(meta["file_type"], "txt")

    def test_extract_txt_with_latin1_encoding_fallback(self):
        # Simulate an older Windows-saved text file using a non-UTF-8 encoding
        content = "Café résumé naïve déjà vu plagiarism test sentence."
        raw_bytes = content.encode("latin-1")
        text, meta = extract_text_from_txt_bytes(raw_bytes)
        self.assertIn("plagiarism test sentence", text)

    def test_missing_txt_raises(self):
        with self.assertRaises(FileNotFoundError):
            extract_text_from_txt(os.path.join(self.tmpdir, "missing.txt"))

    def test_empty_txt_raises_extraction_error(self):
        path = os.path.join(self.tmpdir, "empty.txt")
        fixtures.make_txt(path, "")
        with self.assertRaises(ExtractionError):
            extract_text_from_txt(path)


class TestExtractDispatcher(TestExtractorBase):
    def test_dispatches_pdf_docx_txt_correctly(self):
        pdf_path = os.path.join(self.tmpdir, "a.pdf")
        docx_path = os.path.join(self.tmpdir, "b.docx")
        txt_path = os.path.join(self.tmpdir, "c.txt")
        fixtures.make_pdf(pdf_path, "PDF dispatch sentence with enough words to pass.")
        fixtures.make_docx(docx_path, ["DOCX dispatch sentence with enough words to pass."])
        fixtures.make_txt(txt_path, "TXT dispatch sentence with enough words to pass.")

        text_pdf, meta_pdf = extract_text(pdf_path)
        text_docx, meta_docx = extract_text(docx_path)
        text_txt, meta_txt = extract_text(txt_path)

        self.assertEqual(meta_pdf["file_type"], "pdf")
        self.assertEqual(meta_docx["file_type"], "docx")
        self.assertEqual(meta_txt["file_type"], "txt")

    def test_unsupported_file_type_raises(self):
        path = os.path.join(self.tmpdir, "doc.rtf")
        with open(path, "w") as f:
            f.write("hello")
        with self.assertRaises(UnsupportedFileTypeError):
            extract_text(path)

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            extract_text(os.path.join(self.tmpdir, "does_not_exist.pdf"))

    def test_bytes_without_filename_raises_value_error(self):
        with self.assertRaises(ValueError):
            extract_text(b"some bytes", filename=None)

    def test_bytes_with_unsupported_extension_raises(self):
        with self.assertRaises(UnsupportedFileTypeError):
            extract_text(b"some bytes", filename="notes.rtf")


if __name__ == "__main__":
    unittest.main()
