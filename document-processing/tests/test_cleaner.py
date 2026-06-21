"""
test_cleaner.py
----------------
Tests for cleaner.py: whitespace, hyphenation, page numbers, headers/
footers, citations.
"""

import unittest

from document_preprocessor import clean_text


class TestCleaner(unittest.TestCase):
    def test_collapses_whitespace(self):
        self.assertEqual(
            clean_text("Hello    world.\n\n\n\nBye."),
            "Hello world.\nBye.",
        )

    def test_fixes_hyphenation_across_linebreak(self):
        result = clean_text("This is an exam-\nple of hyphenation.")
        self.assertIn("example", result)
        self.assertNotIn("exam-", result)

    def test_removes_standalone_page_numbers(self):
        result = clean_text("Some content.\n12\nMore content.")
        self.assertNotIn("\n12\n", result)

    def test_removes_repeated_headers(self):
        text = "\n".join(
            [
                "Running Header",
                "First real sentence about biology.",
                "Running Header",
                "Second real sentence about chemistry.",
                "Running Header",
                "Third real sentence about physics.",
            ]
        )
        result = clean_text(text, header_footer_min_repeats=3)
        self.assertNotIn("Running Header", result)
        self.assertIn("biology", result)

    def test_does_not_strip_short_legit_repeats_below_threshold(self):
        text = "Running Header\nReal sentence one.\nRunning Header\nReal sentence two."
        result = clean_text(text, header_footer_min_repeats=3)
        self.assertIn("Running Header", result)

    def test_empty_input_returns_empty_string(self):
        self.assertEqual(clean_text(""), "")

    def test_strip_citations_flag(self):
        result = clean_text("This is a claim [12]. This is another [3, 4].", strip_citations=True)
        self.assertNotIn("[12]", result)
        self.assertNotIn("[3, 4]", result)

    def test_citations_kept_by_default(self):
        result = clean_text("This is a claim [12].")
        self.assertIn("[12]", result)


if __name__ == "__main__":
    unittest.main()
