"""Repository for study document records."""

from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.study_document import StudyDocument
from app.repositories.base import BaseRepository


class StudyDocumentRepository(BaseRepository[StudyDocument, BaseModel, BaseModel]):
    """Data access for the study_documents table."""

    def list_all(
        self, db: Session, *, subject_id: Optional[int] = None
    ) -> List[StudyDocument]:
        """Return documents, optionally filtered by subject."""
        query = db.query(StudyDocument)
        if subject_id is not None:
            query = query.filter(StudyDocument.subject_id == subject_id)
        return query.all()

    def stage_document(
        self,
        db: Session,
        *,
        subject_id: int,
        created_by: int,
        title: str,
        file_path: str,
        file_type: str,
    ) -> StudyDocument:
        """Stage a new study document in the current session (no commit)."""
        db_doc = StudyDocument(
            subject_id=subject_id,
            created_by=created_by,
            title=title,
            file_path=file_path,
            file_type=file_type,
        )
        db.add(db_doc)
        return db_doc


study_document_repository = StudyDocumentRepository(StudyDocument)
