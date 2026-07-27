"""
report_generator.py

Generates a plagiarism report from the assessed matches.
"""


def generate_report(risk_results):
    """
    Generates a formatted plagiarism report.

    Parameters:
        risk_results (list):
            List of tuples
            (doc1_index, doc2_index, similarity_score, risk)

    Returns:
        str:
            Formatted report.
    """

    report = []
    report.append("=" * 60)
    report.append("PLAGIARISM DETECTION REPORT")
    report.append("=" * 60)

    if not risk_results:
        report.append("No plagiarism detected.")
    else:
        for doc1, doc2, score, risk in risk_results:
            report.append(
                f"Document 1 Sentence {doc1 + 1} "
                f"<-> "
                f"Document 2 Sentence {doc2 + 1}"
            )
            report.append(f"Similarity Score : {score:.2f}")
            report.append(f"Risk Level       : {risk}")
            report.append("-" * 60)

    return "\n".join(report)