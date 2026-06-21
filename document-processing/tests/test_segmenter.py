"""
test_segmenter.py
------------------
Tests for segmenter.py: sentence splitting and short-fragment filtering.
"""

import unittest

from document_preprocessor import segment_sentences


class TestSegmenter(unittest.TestCase):
    def test_basic_segmentation(self):
        text = "This is sentence one. This is sentence two. This is sentence three."
        sentences = segment_sentences(text)
        self.assertEqual(len(sentences), 3)

    def test_filters_short_fragments(self):
        text = "Figure 1. This is a real sentence with enough words in it."
        sentences = segment_sentences(text, min_words=4)
        self.assertTrue(all(len(s.split()) >= 4 for s in sentences))
        self.assertFalse(any(s.strip() == "Figure 1." for s in sentences))

    def test_empty_text_returns_empty_list(self):
        self.assertEqual(segment_sentences(""), [])
        self.assertEqual(segment_sentences("   "), [])

    def test_large_text_many_sentences(self):
        # Sanity check for "documents can be any size": 500 short
        # sentences should segment correctly without issue.
        text = " ".join(f"This is test sentence number {i} in a long document." for i in range(500))
        sentences = segment_sentences(text)
        self.assertEqual(len(sentences), 500)


if __name__ == "__main__":
    unittest.main()
