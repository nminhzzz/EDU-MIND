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
        if plan and plan.rag_content:
            logger.info("Sinh đề thi: Sử dụng trực tiếp lý thuyết (rag_content) của study plan %d làm ngữ cảnh.", study_plan_id)
            context = plan.rag_content

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
    include_essay: bool = False,
    essay_count: int = 0,
) -> Quiz:
    """
    Generate a quiz for a classroom via RAG: search related materials or use document_id ->
    AI generates questions -> save to MySQL.
    """
    if document_id:
        doc = study_document_repository.get(db, document_id)
        if not doc:
            raise ValueError(f"Không tìm thấy tài liệu với ID={document_id}")

        # 1. Try fetching pre-chunked embeddings directly from MongoDB in 0.01s
        mongo_chunks = await get_document_chunks_from_mongo(db_mongo, document_id)
        if mongo_chunks:
            logger.info("Directly retrieved %d pre-chunked embeddings from MongoDB for doc #%s in 0.01s!", len(mongo_chunks), document_id)
            context = "\n\n".join(mongo_chunks)[:8000]
            subject = subject_repository.get(db, subject_id)
            if not subject:
                raise ValueError(f"Không tìm thấy môn học với ID={subject_id}")

            topic_str = topic or doc.title
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
            )

            questions_json = normalize_ai_questions(ai_quiz)
            raw_title = (getattr(ai_quiz, "title", None) or "").strip()
            if not raw_title or raw_title == "QuizResponse":
                raw_title = f"Bài tập: {doc.title} ({subject.name})"

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

        # 2. Fallback to Cloudinary reading if MongoDB has no chunks
        try:
            file_bytes, media_type, filename = read_study_document_file(doc)
            return await generate_classroom_quiz_from_file(
                db=db,
                subject_id=subject_id,
                classroom_id=classroom_id,
                file_bytes=file_bytes,
                filename=filename,
                topic=topic or doc.title,
                difficulty=difficulty,
                total_questions=total_questions,
                deadline=deadline,
                time_limit_minutes=time_limit_minutes,
                max_tab_violations=max_tab_violations,
                document_id=document_id,
                include_essay=include_essay,
                essay_count=essay_count,
            )
        except (FileNotFoundError, RuntimeError) as exc:
            logger.warning("Không thể đọc tệp tài liệu #%s (%s), chuyển sang RAG search theo tên bài: %s", document_id, doc.title, exc)
            topic = topic or doc.title

    subject = subject_repository.get(db, subject_id)
    if not subject:
        raise ValueError(f"Không tìm thấy môn học với ID={subject_id}")

    topic_str = topic or "Tổng hợp"
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
    include_essay: bool = False,
    essay_count: int = 0,
) -> Quiz:
    """
    Extract text from an uploaded file (.pdf, .docx, .txt) and use it as RAG context
    to generate an AI quiz for a classroom.
    """
    import os
    import io

    ext = os.path.splitext(filename.lower())[1]
    extracted_text = ""

    if ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            pages = [page.extract_text() for page in reader.pages[:15] if page.extract_text()]
            extracted_text = "\n".join(pages)
        except Exception:
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    pages = [page.extract_text() for page in pdf.pages[:15] if page.extract_text()]
                    extracted_text = "\n".join(pages)
            except Exception:
                pass
    elif ext in [".docx", ".doc"]:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        extracted_text = "\n".join(paragraphs)
    elif ext in [".txt"]:
        extracted_text = file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Định dạng tệp {ext} không được hỗ trợ. Vui lòng tải file PDF, Word hoặc TXT.")

    if not extracted_text.strip():
        raise ValueError("Không thể trích xuất nội dung văn bản từ tệp tin được tải lên.")

    context = extracted_text[:8000]

    subject = subject_repository.get(db, subject_id)
    if not subject:
        raise ValueError(f"Không tìm thấy môn học với ID={subject_id}")

    topic_name = topic or filename
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
    )

    questions_json = normalize_ai_questions(ai_quiz)

    raw_title = (getattr(ai_quiz, "title", None) or "").strip()
    if not raw_title or raw_title == "QuizResponse":
        raw_title = f"Đề thi từ tài liệu: {filename} ({subject.name})"

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
