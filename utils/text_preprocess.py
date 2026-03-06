# smart_contact_audit/utils/text_preprocess.py
import fitz  # PyMuPDF
from docx import Document
from pathlib import Path

def extract_text_from_file(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        doc = fitz.open(file_path)
        return "\n".join(page.get_text() for page in doc)
    elif suffix == ".docx":
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    else:  # .txt
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()