"""
Service xử lý Quiz & Chấm bài thi có RAG — Giai đoạn 3.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.models.subject import Subject
from app.models.question_bank import QuestionBank
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.quiz_attempt import QuizAttempt
from app.schemas.quiz import QuizCreateRequest
from app.schemas.quiz_attempt import QuizAttemptAnswer
from app.agents.quiz_generator.agent import generate_quiz
from app.services.embedding_service import vector_search_materials, get_embedding


async def generate_and_save_quiz(
    db: Session,
    db_mongo: Any,
    classroom_id: int,
    subject_id: int,
    topic: str,
    difficulty: str,
    total_questions: int,
    question_type: str,
    teacher_id: Optional[int] = None
) -> Quiz:
    """
    Sinh đề thi bằng RAG: Tìm tài liệu liên quan trong MongoDB -> AI sinh câu hỏi -> Lưu DB.
    """
    # 1. Kiểm tra môn học tồn tại để lấy tên môn học
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise ValueError(f"Không tìm thấy môn học với ID={subject_id}")

    # 2. RAG: Tìm các tài liệu liên quan trong MongoDB
    materials = await vector_search_materials(
        db_mongo=db_mongo,
        query_text=topic,
        subject_id=subject_id,
        top_k=3
    )

    # Nối nội dung các tài liệu thành ngữ cảnh
    context = ""
    if materials:
        context = "\n\n".join(
            f"--- Tài liệu {i+1} (Chủ đề: {m['topic']}) ---\n{m['content']}"
            for i, m in enumerate(materials)
        )

    # 3. Gọi AI Agent sinh đề thi kèm ngữ cảnh RAG
    ai_quiz = generate_quiz(
        subject=subject.name,
        topic=topic,
        difficulty=difficulty,
        total_questions=total_questions,
        question_type=question_type,
        context=context
    )

    # 4. Lưu đề thi vào MySQL
    db_quiz = Quiz(
        classroom_id=classroom_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        title=ai_quiz.title or f"Bài kiểm tra {subject.name} - {topic}",
        difficulty=difficulty,
        total_questions=len(ai_quiz.questions),
        generated_by_ai=True
    )
    db.add(db_quiz)
    db.flush()  # Lấy db_quiz.id trước để dùng cho bảng junction

    # 5. Lưu câu hỏi vào Question Bank (MySQL) và tạo Embedding cho câu hỏi (MongoDB)
    for q in ai_quiz.questions:
        # Convert options sang định dạng list of dicts
        options_data = [{"key": opt.key, "value": opt.value} for opt in q.options] if q.options else []

        # Sinh embedding cho câu hỏi để lưu vào MongoDB, phục vụ tái sử dụng/tìm kiếm
        try:
            q_vector = get_embedding(q.question_text)
            embedding_doc = {
                "subject_id": subject_id,
                "topic": topic,
                "content": q.question_text,
                "embedding": q_vector,
                "metadata": {"type": "question", "options": options_data},
                "created_at": datetime.utcnow()
            }
            mongo_res = await db_mongo.study_material_embeddings.insert_one(embedding_doc)
            embedding_id = str(mongo_res.inserted_id)
        except Exception:
            embedding_id = None

        # Lưu câu hỏi vào QuestionBank MySQL
        db_qb_question = QuestionBank(
            subject_id=subject_id,
            topic=topic,
            difficulty=q.difficulty or difficulty,
            question_text=q.question_text,
            options=options_data,
            correct_answer=q.correct_answer,
            explanation=q.explanation,
            created_by=teacher_id,
            embedding_id=embedding_id
        )
        db.add(db_qb_question)
        db.flush()

        # Tạo mối quan hệ junction trong bảng questions
        db_junction = Question(
            quiz_id=db_quiz.id,
            question_bank_id=db_qb_question.id
        )
        db.add(db_junction)

    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def submit_quiz_attempt(
    db: Session,
    quiz_id: int,
    student_id: int,
    submitted_answers: List[QuizAttemptAnswer],
    duration_seconds: int
) -> QuizAttempt:
    """
    Chấm điểm bài thi của học sinh và lưu kết quả lượt làm bài (Quiz Attempt).
    """
    # 1. Lấy đề thi kèm các câu hỏi
    quiz = (
        db.query(Quiz)
        .options(joinedload(Quiz.questions).joinedload(Question.question_bank_item))
        .filter(Quiz.id == quiz_id)
        .first()
    )
    if not quiz:
        raise ValueError(f"Không tìm thấy đề thi với ID={quiz_id}")

    # Tạo map tra cứu đáp án đúng của từng câu hỏi trong đề thi
    correct_answers_map = {}
    for q_junction in quiz.questions:
        qb_item = q_junction.question_bank_item
        if qb_item:
            correct_answers_map[qb_item.id] = qb_item.correct_answer

    # 2. Tiến hành chấm bài
    correct_count = 0
    wrong_count = 0
    answers_json = []

    # Map các câu trả lời học sinh nộp
    submitted_map = {ans.question_bank_id: ans.answer for ans in submitted_answers}

    # Duyệt qua các câu hỏi thực tế trong đề để tính điểm
    for q_junction in quiz.questions:
        qb_item = q_junction.question_bank_item
        if not qb_item:
            continue
            
        student_ans = submitted_map.get(qb_item.id, "")
        correct_ans = correct_answers_map.get(qb_item.id, "")
        
        is_correct = (str(student_ans).strip().upper() == str(correct_ans).strip().upper())
        
        if is_correct:
            correct_count += 1
        else:
            wrong_count += 1
            
        answers_json.append({
            "question_bank_id": qb_item.id,
            "answer": student_ans,
            "is_correct": is_correct
        })

    # 3. Tính điểm trên thang điểm 10.0
    total_q = len(correct_answers_map)
    score = (correct_count / total_q * 10.0) if total_q > 0 else 0.0

    # 4. Lưu lượt làm bài vào MySQL
    db_attempt = QuizAttempt(
        quiz_id=quiz_id,
        student_id=student_id,
        answers=answers_json,
        score=score,
        correct_count=correct_count,
        wrong_count=wrong_count,
        duration_seconds=duration_seconds
    )
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)

    return db_attempt
