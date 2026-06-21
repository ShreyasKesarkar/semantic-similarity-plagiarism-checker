"""
test_validators.py
-------------------
Tests for validators.py: file type checking and basic sanity checks.
"""

import os
import tempfile
import unittest

from document_preprocessor import (
    SUPPORTED_EXTENSIONS,
    is_supported_filename,
    validate_filename,
    UnsupportedFileTypeError,
)
from document_preprocessor.validators import validate_not_empty, validate_max_size
from document_preprocessor.exceptions import ValidationError


class TestSupportedExtensions(unittest.TestCase):
    def test_supported_extensions_are_pdf_docx_txt_only(self):
        self.assertEqual(SUPPORTED_EXTENSIONS, {".pdf", ".docx", ".txt"})

    def test_is_supported_filename_true_cases(self):
        for name in ["essay.pdf", "essay.DOCX", "notes.txt", "ESSAY.Pdf"]:
            self.assertTrue(is_supported_filename(name), msg=name)

    def test_is_supported_filename_false_cases(self):
        for name in ["essay.doc", "essay.png", "essay.zip", "essay", "essay.rtf"]:
            self.assertFalse(is_supported_filename(name), msg=name)


class TestValidateFilename(unittest.TestCase):
    def test_accepts_supported_types(self):
        for name in ["essay.pdf", "essay.docx", "essay.txt"]:
            validate_filename(name)  # should not raise

    def test_rejects_unsupported_types(self):
        for name in ["essay.doc", "image.png", "archive.zip", "essay.rtf"]:
            with self.assertRaises(UnsupportedFileTypeError):
                validate_filename(name)

    def test_rejects_no_extension(self):
        with self.assertRaises(UnsupportedFileTypeError):
            validate_filename("essay_no_extension")


class TestValidateNotEmpty(unittest.TestCase):
    def test_empty_bytes_raises(self):
        with self.assertRaises(ValidationError):
            validate_not_empty(b"")

    def test_nonempty_bytes_ok(self):
        validate_not_empty(b"some content")  # should not raise

    def test_empty_file_on_disk_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "empty.txt")
            open(path, "w").close()
            with self.assertRaises(ValidationError):
                validate_not_empty(path)

    def test_nonempty_file_on_disk_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "notempty.txt")
            with open(path, "w") as f:
                f.write("hello")
            validate_not_empty(path)  # should not raise


class TestValidateMaxSize(unittest.TestCase):
    def test_no_limit_by_default(self):
        # Documents can be any size per project requirements -- huge
        # size should pass when max_size_mb is None (the default).
        validate_max_size(500 * 1024 * 1024, max_size_mb=None)

    def test_under_limit_ok(self):
        validate_max_size(1 * 1024 * 1024, max_size_mb=10)  # 1MB under a 10MB cap

    def test_over_limit_raises(self):
        with self.assertRaises(ValidationError):
            validate_max_size(20 * 1024 * 1024, max_size_mb=10)  # 20MB over a 10MB cap


if __name__ == "__main__":
    unittest.main()
