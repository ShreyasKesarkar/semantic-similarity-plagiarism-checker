from threshold import filter_matches

matches = [
    (0, 0, 0.95),
    (1, 2, 0.76),
    (2, 1, 0.88),
    (3, 3, 0.45),
]

result = filter_matches(matches)

print("Filtered Matches:")
for item in result:
    print(item)