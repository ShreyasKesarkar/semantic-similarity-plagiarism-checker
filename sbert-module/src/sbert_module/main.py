from document_preprocessor.pipeline import process_document_pair
from sbert_module.pipeline import compare_processed_documents

processed_documents = process_document_pair(
    r"C:\Users\Manaswini\Desktop\summer internship\cloned_repo\document-processing\sample_files\sample_document.pdf",
    r"C:\Users\Manaswini\Desktop\summer internship\cloned_repo\document-processing\sample_files\sample_document.docx",
)

result = compare_processed_documents(processed_documents)

print(result)