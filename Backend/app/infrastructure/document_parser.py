"""
Document text extraction — PDF and DOCX adapters.
"""

import io

from docx import Document
from pypdf import PdfReader

from app.core.logging import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF file."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text_content = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_content.append(text)
        return "\n".join(text_content).strip()
    except Exception as exc:
        logger.warning("Failed to parse PDF file: %s", exc)
        return ""


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract plain text from a Word (.docx) file."""
    try:
        doc = Document(io.BytesIO(file_bytes))
        text_content = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(text_content).strip()
    except Exception as exc:
        logger.warning("Failed to parse DOCX file: %s", exc)
        return ""
