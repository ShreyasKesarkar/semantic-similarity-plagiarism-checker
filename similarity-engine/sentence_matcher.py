"""
sentence_matcher.py

Finds the best matching sentence in Document 2
for every sentence in Document 1.
"""

import numpy as np


def find_best_matches(similarity_matrix):
    """
    Finds the best match for every sentence.

    Parameters:
        similarity_matrix (numpy.ndarray):
            Matrix returned by cosine similarity.

    Returns:
        list:
            List of tuples
            (doc1_sentence_index,
             doc2_sentence_index,
             similarity_score)
    """

    matches = []

    for i in range(similarity_matrix.shape[0]):
        best_match = int(np.argmax(similarity_matrix[i]))
        best_score = similarity_matrix[i][best_match]

        matches.append(
            (i, best_match, float(best_score))
        )

    return matches