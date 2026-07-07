import io
from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Trích xuất toàn bộ văn bản (text content) từ tệp PDF.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text_content = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_content.append(text)
        return "\n".join(text_content).strip()
    except Exception as e:
        print(f"[Warning] Failed to parse PDF file: {e}")
        return ""


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Trích xuất toàn bộ văn bản (text content) từ tệp Word (.docx).
    """
    try:
        doc = Document(io.BytesIO(file_bytes))
        text_content = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text)
        return "\n".join(text_content).strip()
    except Exception as e:
        print(f"[Warning] Failed to parse DOCX file: {e}")
        return ""
