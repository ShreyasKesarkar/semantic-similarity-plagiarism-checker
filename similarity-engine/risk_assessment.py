"""
risk_assessment.py

Assigns plagiarism risk levels based on similarity scores.
"""


def assess_risk(filtered_matches):
    """
    Assigns a risk level to each filtered match.

    Parameters:
        filtered_matches (list):
            List of tuples
            (doc1_index, doc2_index, similarity_score)

    Returns:
        list:
            (doc1_index, doc2_index, similarity_score, risk_level)
    """

    results = []

    for doc1_idx, doc2_idx, score in filtered_matches:

        if score >= 0.95:
            risk = "High"

        elif score >= 0.85:
            risk = "Medium"

        else:
            risk = "Low"

        results.append(
            (doc1_idx, doc2_idx, score, risk)
        )

    return results