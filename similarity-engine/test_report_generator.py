from report_generator import generate_report

results = [
    (0, 0, 0.98, "High"),
    (1, 2, 0.89, "Medium"),
    (2, 1, 0.82, "Low"),
]

report = generate_report(results)

print(report)