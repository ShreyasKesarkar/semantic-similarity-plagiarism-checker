from document_preprocessor import process_document_pair

result = process_document_pair(
    "sample_files/sample_document.pdf",
    "sample_files/sample_document.docx",
)

print(result["document_a"]["sentences"])   # list of clean sentences from Doc A
print(result["document_b"]["sentences"])   # list of clean sentences from Doc B