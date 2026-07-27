"""
threshold.py

Filters sentence matches based on a similarity threshold.
"""


def filter_matches(matches, threshold=0.80):
    """
    Filters sentence matches that exceed the similarity threshold.

    Parameters:
        matches (list):
            List of tuples
            (doc1_index, doc2_index, similarity_score)

        threshold (float):
            Minimum similarity required to be considered plagiarism.

    Returns:
        list:
            Filtered matches.
    """

    filtered = []

    for match in matches:
        if match[2] >= threshold:
            filtered.append(match)

    return filtered