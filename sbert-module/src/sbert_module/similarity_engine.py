from sklearn.metrics.pairwise import cosine_similarity
from .sbert_service import get_embedding

def compare_sentences(text1, text2):

    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)

    score = cosine_similarity([emb1], [emb2])[0][0]

    return score

