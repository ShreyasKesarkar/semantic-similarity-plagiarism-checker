import numpy as np
from sentence_matcher import find_best_matches

similarity_matrix = np.array([
    [1.00, 0.95],
    [0.97, 0.99]
])

matches = find_best_matches(similarity_matrix)

print("Best Matches:")
for match in matches:
    print(match)