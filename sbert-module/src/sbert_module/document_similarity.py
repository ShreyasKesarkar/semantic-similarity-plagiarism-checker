from .sbert_service import MODEL_NAME, get_embeddings
from .risk_engine import get_risk
from sklearn.metrics.pairwise import cosine_similarity


def compare_documents(doc1_sentences, doc2_sentences):
    if not doc1_sentences or not doc2_sentences:
      return {
        "model": MODEL_NAME,
        "overall_similarity": 0.0,
        "risk_level": "LOW",
        "document_a_sentence_count": len(doc1_sentences),
        "document_b_sentence_count": len(doc2_sentences),
        "matched_sentences": []
    }

    # Generate embeddings only once
    embeddings1 = get_embeddings(doc1_sentences)
    embeddings2 = get_embeddings(doc2_sentences)

    matches = []
    best_scores = []

    for i, emb1 in enumerate(embeddings1):

        similarities = cosine_similarity([emb1], embeddings2)[0]

        best_index = similarities.argmax()

        max_score = float(similarities[best_index])

        best_scores.append(max_score)

        matches.append({
            "sentence_a": doc1_sentences[i],
            "sentence_b": doc2_sentences[best_index],
            "score": round(max_score, 4)
        })

    overall_similarity = (
    sum(best_scores) / len(best_scores)
    ) * 100

    overall_similarity = round(overall_similarity, 2)

    risk_level = get_risk(overall_similarity)

    return {
        "model": MODEL_NAME,
        "overall_similarity": overall_similarity,
        "risk_level": risk_level,
        "document_a_sentence_count": len(doc1_sentences),
        "document_b_sentence_count": len(doc2_sentences),
        "matched_sentences": matches
}