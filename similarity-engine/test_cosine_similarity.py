import numpy as np
from cosine_similarity import calculate_similarity

# Dummy embeddings (simulating Member 3's output)

doc1_embeddings = np.array([
    [0.1, 0.2, 0.3],
    [0.4, 0.5, 0.6]
])

doc2_embeddings = np.array([
    [0.1, 0.2, 0.3],
    [0.7, 0.8, 0.9]
])

similarity_matrix = calculate_similarity(
    doc1_embeddings,
    doc2_embeddings
)

print("Similarity Matrix:")
print(similarity_matrix)