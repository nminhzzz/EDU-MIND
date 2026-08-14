"""
AI quiz generation with RAG context.
"""

import asyncio
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.unit_of_work import commit_or_rollback
from app.models.quiz import Quiz
from app.repositories.quiz_repository import quiz_repository
from app.repositories.subject_repository import subject_repository
from app.repositories.study_document_repository import study_document_repository
from app.services.study_document_service import read_study_document_file
from app.services.embedding_service import vector_search_materials, get_document_chunks_from_mongo
from app.services.quiz.agent_port import quiz_generator
from app.services.quiz.grading import build_rag_context, normalize_ai_questions

logger = get_logger(__name__)


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
    RAG-grounded quiz generation for students -> saves to MySQL.
    """
    subject = subject_repository.get(db, subject_id)
    if not subject:
        raise ValueError(f"Không tìm thấy môn học với ID={subject_id}")

    context = ""
    if study_plan_id:
        from app.models.study_plan import StudyPlan
        plan = db.query(StudyPlan).filter(StudyPlan.id == study_plan_id).first()
        if plan and (plan.lesson_summary or plan.rag_content):
            logger.info("Sinh đề thi: Sử dụng trực tiếp lý thuyết (rag_content) của study plan %d làm ngữ cảnh.", study_plan_id)
            context = plan.lesson_summary or plan.rag_content[:6000]

    if not context:
        logger.info("Sinh đề thi: Không có rag_content sẵn, chạy tìm kiếm vector MongoDB cho chủ đề: %s", topic)
        materials = await vector_search_materials(
            db_mongo=db_mongo, query_text=topic, subject_id=subject_id, top_k=3
        )
        context = build_rag_context(materials)

    essay_count = max(1, round(total_questions * 0.3))
    ai_quiz = await asyncio.to_thread(
        quiz_generator.generate,
        subject=subject.name,
        topic=topic,
        difficulty=difficulty,
        total_questions=total_questions,
        question_type="mixed",
        context=context,
        essay_count=essay_count,
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


def _extract_text_from_file_bytes(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from an uploaded file (.pdf, .docx, .txt)."""
    import os
    import io

    ext = os.path.splitext(filename.lower())[1]
    if ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            pages = [page.extract_text() for page in reader.pages[:15] if page.extract_text()]
            return "\n".join(pages)
        except Exception:
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    pages = [page.extract_text() for page in pdf.pages[:15] if page.extract_text()]
                    return "\n".join(pages)
            except Exception:
                return ""
    elif ext in [".docx", ".doc"]:
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n".join(paragraphs)
        except Exception:
            return ""
    elif ext in [".txt"]:
        return file_bytes.decode("utf-8", errors="ignore")
    return ""


async def generate_classroom_quiz(
    db: Session,
    db_mongo: Any,
    subject_id: int,
    classroom_id: int,
    topic: Optional[str] = None,
    difficulty: str = "medium",
    total_questions: int = 5,
    deadline: Optional[datetime] = None,
    time_limit_minutes: Optional[int] = 30,
    max_tab_violations: Optional[int] = 3,
    document_id: Optional[int] = None,
    document_ids: Optional[list] = None,
    custom_prompt: Optional[str] = None,
    include_essay: bool = False,
    essay_count: int = 0,
) -> Quiz:
    """
    Generate a quiz for a classroom via RAG: search related materials or use document_ids / document_id ->
    AI generates questions -> save to MySQL.
    """
    doc_id_list = []
    if document_ids:
        doc_id_list = [d for d in document_ids if d]
    elif document_id:
        doc_id_list = [document_id]

    context = ""
    primary_doc_id = doc_id_list[0] if doc_id_list else None
    primary_doc_title = None

    if doc_id_list:
        combined_chunks = []
        for d_id in doc_id_list:
            doc = study_document_repository.get(db, d_id)
            if not doc:
                continue
            if not primary_doc_title:
                primary_doc_title = doc.title

            mongo_chunks = await get_document_chunks_from_mongo(db_mongo, d_id)
            if mongo_chunks:
                combined_chunks.extend(mongo_chunks)
            else:
                try:
                    file_bytes, media_type, filename = read_study_document_file(doc)
                    extracted = _extract_text_from_file_bytes(file_bytes, filename)
                    if extracted.strip():
                        combined_chunks.append(extracted)
                except Exception as exc:
                    logger.warning("Không thể đọc tệp tài liệu #%s (%s): %s", d_id, doc.title, exc)

        if combined_chunks:
            context = "\n\n".join(combined_chunks)[:12000]

    subject = subject_repository.get(db, subject_id)
    if not subject:
        raise ValueError(f"Không tìm thấy môn học với ID={subject_id}")

    topic_str = topic or primary_doc_title or "Tổng hợp"

    if not context:
        materials = await vector_search_materials(
            db_mongo=db_mongo, query_text=topic_str, subject_id=subject_id, top_k=3
        )
        context = build_rag_context(materials)

    question_type = "mixed" if (include_essay and essay_count > 0) else "mcq"

    ai_quiz = await asyncio.to_thread(
        quiz_generator.generate,
        subject=subject.name,
        topic=topic_str,
        difficulty=difficulty,
        total_questions=total_questions,
        question_type=question_type,
        context=context,
        essay_count=essay_count if include_essay else 0,
        custom_prompt=custom_prompt,
    )

    questions_json = normalize_ai_questions(ai_quiz)

    raw_title = (getattr(ai_quiz, "title", None) or "").strip()
    if not raw_title or raw_title == "QuizResponse":
        raw_title = f"Bài tập: {topic_str} ({subject.name})"

    db_quiz = quiz_repository.stage_classroom_quiz(
        db,
        subject_id=subject_id,
        classroom_id=classroom_id,
        title=raw_title,
        difficulty=difficulty,
        questions=questions_json,
        deadline=deadline,
        time_limit_minutes=time_limit_minutes,
        max_tab_violations=max_tab_violations,
        document_id=primary_doc_id,
        generated_by_ai=True,
    )

    commit_or_rollback(db)
    db.refresh(db_quiz)
    return db_quiz


async def generate_classroom_quiz_from_files(
    db: Session,
    subject_id: int,
    classroom_id: int,
    files: list,  # List of tuples: [(file_bytes, filename), ...]
    topic: Optional[str] = None,
    difficulty: str = "medium",
    total_questions: int = 5,
    deadline: Optional[datetime] = None,
    time_limit_minutes: Optional[int] = 30,
    max_tab_violations: Optional[int] = 3,
    document_id: Optional[int] = None,
    custom_prompt: Optional[str] = None,
    include_essay: bool = False,
    essay_count: int = 0,
) -> Quiz:
    """
    Extract text from multiple uploaded files (.pdf, .docx, .txt) and use it as RAG context
    to generate an AI quiz for a classroom.
    """
    if not files:
        raise ValueError("Vui lòng tải lên ít nhất 1 tệp tài liệu.")

    extracted_texts = []
    file_names = []

    for file_bytes, filename in files:
        text = _extract_text_from_file_bytes(file_bytes, filename)
        if text.strip():
            extracted_texts.append(f"--- Tài liệu: {filename} ---\n{text.strip()}")
            file_names.append(filename)

    if not extracted_texts:
        raise ValueError("Không thể trích xuất nội dung văn bản từ các tệp tin được tải lên.")

    context = "\n\n".join(extracted_texts)[:12000]

    subject = subject_repository.get(db, subject_id)
    if not subject:
        raise ValueError(f"Không tìm thấy môn học với ID={subject_id}")

    first_filename = file_names[0] if file_names else "tai_lieu.pdf"
    topic_name = topic or (f"{first_filename} + {len(file_names)-1} tệp" if len(file_names) > 1 else first_filename)
    question_type = "mixed" if (include_essay and essay_count > 0) else "mcq"

    ai_quiz = await asyncio.to_thread(
        quiz_generator.generate,
        subject=subject.name,
        topic=topic_name,
        difficulty=difficulty,
        total_questions=total_questions,
        question_type=question_type,
        context=context,
        essay_count=essay_count if include_essay else 0,
        custom_prompt=custom_prompt,
    )

    questions_json = normalize_ai_questions(ai_quiz)

    raw_title = (getattr(ai_quiz, "title", None) or "").strip()
    if not raw_title or raw_title == "QuizResponse":
        raw_title = f"Đề thi từ tài liệu ({subject.name})"

    db_quiz = quiz_repository.stage_classroom_quiz(
        db,
        subject_id=subject_id,
        classroom_id=classroom_id,
        title=raw_title,
        difficulty=difficulty,
        questions=questions_json,
        deadline=deadline,
        time_limit_minutes=time_limit_minutes,
        max_tab_violations=max_tab_violations,
        document_id=document_id,
        generated_by_ai=True,
    )

    commit_or_rollback(db)
    db.refresh(db_quiz)
    return db_quiz


async def generate_classroom_quiz_from_file(
    db: Session,
    subject_id: int,
    classroom_id: int,
    file_bytes: bytes,
    filename: str,
    topic: Optional[str] = None,
    difficulty: str = "medium",
    total_questions: int = 5,
    deadline: Optional[datetime] = None,
    time_limit_minutes: Optional[int] = 30,
    max_tab_violations: Optional[int] = 3,
    document_id: Optional[int] = None,
    custom_prompt: Optional[str] = None,
    include_essay: bool = False,
    essay_count: int = 0,
) -> Quiz:
    """Wrapper for backward compatibility single file generation."""
    return await generate_classroom_quiz_from_files(
        db=db,
        subject_id=subject_id,
        classroom_id=classroom_id,
        files=[(file_bytes, filename)],
        topic=topic,
        difficulty=difficulty,
        total_questions=total_questions,
        deadline=deadline,
        time_limit_minutes=time_limit_minutes,
        max_tab_violations=max_tab_violations,
        document_id=document_id,
        custom_prompt=custom_prompt,
        include_essay=include_essay,
        essay_count=essay_count,
    )
