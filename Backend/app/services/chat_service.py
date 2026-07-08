"""
AI tutor chat session use cases.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.agents.chat_tutor.memory import create_tutor_session
from app.services.subject_service import get_subject


async def create_student_tutor_session(
    db: Session,
    *,
    student_id: int,
    subject_id: int,
    title: Optional[str] = None,
) -> str:
    """Create a tutor chat session after validating the subject exists."""
    subject = get_subject(db, subject_id)
    session_title = title or f"Trò chuyện môn {subject.name}"

    return await create_tutor_session(
        student_id=student_id,
        subject_id=subject.id,
        title=session_title,
    )
