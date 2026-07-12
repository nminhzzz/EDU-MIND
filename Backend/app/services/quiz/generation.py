"""
AI quiz generation with RAG context and multi-agent QC review.
"""

import asyncio
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.unit_of_work import commit_or_rollback
from app.models.quiz import Quiz
from app.repositories.quiz_repository import quiz_repository
from app.repositories.subject_repository import subject_repository
from app.services.embedding_service import vector_search_materials
from app.services.quiz.agent_port import quiz_generator
from app.services.quiz.grading import build_rag_context, normalize_ai_questions

logger = get_logger(__name__)


async def _generate_with_qc_review(
    *,
    subject_name: str,
    topic: str,
    difficulty: str,
    total_questions: int,
    context: str,
    skip_qc: bool = False,
) -> Any:
    """Run quiz generation with optional QC review and correction."""
    ai_quiz = await asyncio.to_thread(
        quiz_generator.generate,
        subject=subject_name,
        topic=topic,
        difficulty=difficulty,
        total_questions=total_questions,
        question_type="mcq",
        context=context,
    )

    if skip_qc:
        return ai_quiz

    try:
        quiz_dict = (
            ai_quiz.model_dump() if hasattr(ai_quiz, "model_dump") else ai_quiz.dict()
        )

        logger.info("Multi-Agent: sending quiz '%s' to QC Reviewer...", topic)
        review = await asyncio.to_thread(
            quiz_generator.review, quiz_data=quiz_dict, context=context
        )

        if not review.is_valid:
            logger.warning(
                "Multi-Agent: QC found issues — '%s'. Requesting correction...",
                review.feedback,
            )
            ai_quiz = await asyncio.to_thread(
                quiz_generator.correct,
                original_quiz=quiz_dict,
                feedback=review.feedback
                or "Hãy tinh chỉnh các câu hỏi cho hay và chính xác hơn.",
                context=context,
            )
            logger.info("Multi-Agent: quiz corrected and finalised.")
        else:
            logger.info("Multi-Agent: QC approved — quiz quality is excellent.")
    except Exception as exc:
        logger.warning(
            "Multi-Agent QC error — skipping review to maintain progress: %s", exc
        )

    return ai_quiz


async def generate_and_save_quiz(
    db: Session,
    db_mongo: Any,
    student_id: int,
    subject_id: int,
    topic: str,
    difficulty: str,
    total_questions: int,
    study_plan_id: Optional[int] = None,
) -> Quiz:
    """
    Generate a quiz via RAG: find related materials in MongoDB → AI generates
    questions → optional QC review → save to MySQL.
    """
    subject = subject_repository.get(db, subject_id)
    if not subject:
        raise ValueError(f"Không tìm thấy môn học với ID={subject_id}")

    materials = await vector_search_materials(
        db_mongo=db_mongo, query_text=topic, subject_id=subject_id, top_k=3
    )
    context = build_rag_context(materials)

    ai_quiz = await _generate_with_qc_review(
        subject_name=subject.name,
        topic=topic,
        difficulty=difficulty,
        total_questions=total_questions,
        context=context,
        skip_qc=False,
    )

    questions_json = normalize_ai_questions(ai_quiz)

    raw_title = (getattr(ai_quiz, "title", None) or "").strip()
    if not raw_title or raw_title == "QuizResponse":
        raw_title = (
            f"Kiểm tra {topic}"
            if study_plan_id
            else f"Đề luyện thi {subject.name} - {topic}"
        )

    db_quiz = quiz_repository.stage_ai_generated(
        db,
        student_id=student_id,
        subject_id=subject_id,
        study_plan_id=study_plan_id,
        title=raw_title,
        difficulty=difficulty,
        questions=questions_json,
    )

    commit_or_rollback(db)
    db.refresh(db_quiz)
    return db_quiz
