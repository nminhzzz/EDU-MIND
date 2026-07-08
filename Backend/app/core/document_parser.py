"""Backward-compatible re-exports — prefer app.infrastructure.document_parser."""

from app.infrastructure.document_parser import (  # noqa: F401
    extract_text_from_docx,
    extract_text_from_pdf,
)
