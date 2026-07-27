from risk_assessment import assess_risk

matches = [
    (0, 0, 0.98),
    (1, 2, 0.90),
    (2, 1, 0.82),
]

results = assess_risk(matches)

print("Risk Assessment:")

for item in results:
    print(item)