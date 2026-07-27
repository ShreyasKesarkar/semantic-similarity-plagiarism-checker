"""
cosine_similarity.py

Calculates cosine similarity between two sets of sentence embeddings.
"""

from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(embeddings_doc1, embeddings_doc2):
    """
    Calculates cosine similarity between two embedding matrices.

    Parameters:
        embeddings_doc1 (list or numpy array):
            Sentence embeddings of Document 1.

        embeddings_doc2 (list or numpy array):
            Sentence embeddings of Document 2.

    Returns:
        similarity_matrix:
            A matrix containing similarity scores
            between every sentence pair.
    """

    similarity_matrix = cosine_similarity(
        embeddings_doc1,
        embeddings_doc2
    )

    return similarity_matrix