"""
test_pipeline.py
-----------------
End-to-end integration tests for pipeline.py: the full
extract -> clean -> segment flow, for all 3 file types, both input
modes (path / bytes), plus validation and the Document A/B pair flow
that mirrors the real teacher-facing use case.
"""

import os
import shutil
import tempfile
import unittest

from document_preprocessor import (
    process_document,
    process_document_pair,
    UnsupportedFileTypeError,
    ValidationError,
)

from . import fixtures


class TestPipelineBase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)


class TestProcessDocumentPathBased(TestPipelineBase):
    def test_full_pipeline_docx(self):
        path = os.path.join(self.tmpdir, "essay.docx")
        fixtures.make_docx(
            path,
            [
                "Photosynthesis is the process by which green plants convert sunlight into chemical energy.",
                "This process occurs primarily in the chloroplasts of plant cells.",
            ],
        )
        result = process_document(path)
        self.assertEqual(result["file_type"], "docx")
        self.assertEqual(result["sentence_count"], 2)
        self.assertEqual(len(result["sentences"]), 2)
        self.assertIn("document_id", result)
        self.assertIn("processed_at", result)
        self.assertIsNotNone(result["source_path"])

    def test_full_pipeline_pdf(self):
        path = os.path.join(self.tmpdir, "essay.pdf")
        fixtures.make_pdf(
            path,
            "Quantum computing leverages superposition and entanglement to perform certain "
            "calculations far more efficiently than classical computers ever could.",
        )
        result = process_document(path)
        self.assertEqual(result["file_type"], "pdf")
        self.assertGreaterEqual(result["sentence_count"], 1)

    def test_full_pipeline_txt(self):
        path = os.path.join(self.tmpdir, "essay.txt")
        fixtures.make_txt(
            path,
            "Neural networks are loosely inspired by the structure of the human brain. "
            "Each layer transforms its input before passing it to the next layer.",
        )
        result = process_document(path)
        self.assertEqual(result["file_type"], "txt")
        self.assertGreaterEqual(result["sentence_count"], 1)

    def test_custom_document_id(self):
        path = os.path.join(self.tmpdir, "essay.docx")
        fixtures.make_docx(path, ["A sentence with enough words to pass the filter."])
        result = process_document(path, document_id="StudentSubmission_42")
        self.assertEqual(result["document_id"], "StudentSubmission_42")

    def test_unsupported_file_type_rejected(self):
        path = os.path.join(self.tmpdir, "essay.rtf")
        with open(path, "w") as f:
            f.write("some content")
        with self.assertRaises(UnsupportedFileTypeError):
            process_document(path)


class TestProcessDocumentBytesBased(TestPipelineBase):
    """Mirrors how the FastAPI backend will actually call this module:
    bytes straight from an UploadFile, no temp file saved anywhere."""

    def test_process_document_from_docx_bytes(self):
        path = os.path.join(self.tmpdir, "essay.docx")
        fixtures.make_docx(
            path, ["This sentence should survive the full bytes-based pipeline run."]
        )
        with open(path, "rb") as f:
            file_bytes = f.read()

        result = process_document(file_bytes, filename="essay.docx")
        self.assertEqual(result["document_id"], "essay.docx")
        self.assertIsNone(result["source_path"])  # no path exists for in-memory input
        self.assertGreaterEqual(result["sentence_count"], 1)

    def test_process_document_from_txt_bytes(self):
        content = "Machine translation has improved significantly with transformer models."
        result = process_document(content.encode("utf-8"), filename="essay.txt")
        self.assertEqual(result["file_type"], "txt")
        self.assertGreaterEqual(result["sentence_count"], 1)

    def test_bytes_without_filename_raises(self):
        with self.assertRaises(ValueError):
            process_document(b"some bytes")


class TestProcessDocumentValidation(TestPipelineBase):
    def test_empty_file_rejected(self):
        path = os.path.join(self.tmpdir, "empty.txt")
        fixtures.make_txt(path, "")
        with self.assertRaises(ValidationError):
            process_document(path)

    def test_empty_bytes_rejected(self):
        with self.assertRaises(ValidationError):
            process_document(b"", filename="empty.txt")

    def test_max_size_mb_enforced_when_set(self):
        path = os.path.join(self.tmpdir, "essay.txt")
        fixtures.make_txt(path, "A sentence with enough words to pass the filter easily.")
        # File is tiny, so a 0.000001 MB cap should reject it
        with self.assertRaises(ValidationError):
            process_document(path, max_size_mb=0.000001)

    def test_no_size_limit_by_default(self):
        path = os.path.join(self.tmpdir, "essay.txt")
        fixtures.make_txt(path, "A sentence with enough words to pass the filter easily.")
        result = process_document(path)  # max_size_mb defaults to None -> no limit
        self.assertGreaterEqual(result["sentence_count"], 1)


class TestProcessDocumentPair(TestPipelineBase):
    def test_process_document_pair_both_paths(self):
        path_a = os.path.join(self.tmpdir, "a.docx")
        path_b = os.path.join(self.tmpdir, "b.docx")
        fixtures.make_docx(path_a, ["This is document A with a unique sentence about cats."])
        fixtures.make_docx(path_b, ["This is document B with a unique sentence about dogs."])

        result = process_document_pair(path_a, path_b)
        self.assertIn("document_a", result)
        self.assertIn("document_b", result)
        self.assertEqual(result["document_a"]["document_id"], "Document A")
        self.assertEqual(result["document_b"]["document_id"], "Document B")

    def test_process_document_pair_mixed_path_and_bytes(self):
        # Mirrors a realistic scenario: Document A already on disk,
        # Document B freshly uploaded as bytes.
        path_a = os.path.join(self.tmpdir, "a.docx")
        fixtures.make_docx(path_a, ["Document A sentence about elephants and habitats."])

        path_b = os.path.join(self.tmpdir, "b.docx")
        fixtures.make_docx(path_b, ["Document B sentence about elephants and habitats."])
        with open(path_b, "rb") as f:
            bytes_b = f.read()

        result = process_document_pair(path_a, bytes_b, filename_b="b.docx")
        self.assertEqual(result["document_a"]["document_id"], "Document A")
        self.assertEqual(result["document_b"]["document_id"], "Document B")
        self.assertGreaterEqual(result["document_b"]["sentence_count"], 1)

    def test_process_document_pair_mixed_file_types(self):
        # Document A is a PDF, Document B is a TXT -- different formats
        # should compare without issue since both produce the same
        # output schema.
        path_a = os.path.join(self.tmpdir, "a.pdf")
        path_b = os.path.join(self.tmpdir, "b.txt")
        fixtures.make_pdf(path_a, "Renewable energy adoption has accelerated across the globe.")
        fixtures.make_txt(path_b, "Renewable energy adoption has accelerated across the globe.")

        result = process_document_pair(path_a, path_b)
        self.assertEqual(result["document_a"]["file_type"], "pdf")
        self.assertEqual(result["document_b"]["file_type"], "txt")


class TestLargeDocument(TestPipelineBase):
    """Confirms the 'documents can be any size' requirement holds up in
    practice -- a 40-page PDF and a long DOCX both process correctly."""

    def test_large_multipage_pdf(self):
        path = os.path.join(self.tmpdir, "large.pdf")
        # Unique text per page -- using identical text on every page would
        # (correctly) get stripped by header/footer noise removal, since
        # that's indistinguishable from a real repeated running header.
        page_texts = [
            f"This page discusses topic number {i} of the research in considerable detail."
            for i in range(40)
        ]
        fixtures.make_pdf_with_unique_pages(path, page_texts)

        result = process_document(path)
        self.assertEqual(result["extraction_metadata"]["num_pages"], 40)
        self.assertGreaterEqual(result["sentence_count"], 40)

    def test_large_docx_many_paragraphs(self):
        path = os.path.join(self.tmpdir, "large.docx")
        paragraphs = [
            f"This is paragraph number {i} discussing topic {i} in the document." for i in range(300)
        ]
        fixtures.make_docx(path, paragraphs)
        result = process_document(path)
        self.assertEqual(result["sentence_count"], 300)


if __name__ == "__main__":
    unittest.main()
