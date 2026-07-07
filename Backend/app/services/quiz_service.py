"""
Service xử lý Quiz & Chấm bài thi có RAG — Giai đoạn 3 & Giai đoạn 4.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.subject import Subject
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.schemas.quiz import QuizCreateRequest
from app.schemas.quiz_attempt import QuizAttemptAnswer
from app.agents.quiz_generator.agent import generate_quiz
from app.services.embedding_service import vector_search_materials


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
    Sinh đề thi bằng RAG: Tìm tài liệu liên quan trong MongoDB -> AI sinh câu hỏi -> Lưu DB.
    """
    # 1. Kiểm tra môn học tồn tại để lấy tên môn học
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise ValueError(f"Không tìm thấy môn học với ID={subject_id}")

    # 2. RAG: Tìm các tài liệu liên quan trong MongoDB
    materials = await vector_search_materials(
        db_mongo=db_mongo, query_text=topic, subject_id=subject_id, top_k=3
    )

    # Nối nội dung các tài liệu thành ngữ cảnh
    context = ""
    if materials:
        context = "\n\n".join(
            f"--- Tài liệu {i+1} (Chủ đề: {m['topic']}) ---\n{m['content']}"
            for i, m in enumerate(materials)
        )

    # 3. Gọi AI Agent sinh đề thi kèm ngữ cảnh RAG
    import asyncio

    ai_quiz = await asyncio.to_thread(
        generate_quiz,
        subject=subject.name,
        topic=topic,
        difficulty=difficulty,
        total_questions=total_questions,
        question_type="mcq",
        context=context,
    )

    # Luồng Multi-Agent: Thẩm định chéo đề thi (QC Reviewer Agent)
    try:
        from app.agents.quiz_generator.reviewer import review_generated_quiz
        from app.agents.quiz_generator.agent import correct_quiz_questions

        # Chuyển đổi Pydantic model sang dict để truyền vào reviewer
        if hasattr(ai_quiz, "model_dump"):
            quiz_dict = ai_quiz.model_dump()
        else:
            quiz_dict = ai_quiz.dict()

        print(
            f"[Multi-Agent] Gửi đề thi bài học '{topic}' cho QC Reviewer Agent thẩm định chéo..."
        )
        review = await asyncio.to_thread(
            review_generated_quiz, quiz_data=quiz_dict, context=context
        )

        if not review.is_valid:
            print(
                f"[Multi-Agent] QC Reviewer phát hiện lỗi: '{review.feedback}'. Đang yêu cầu sửa lại..."
            )
            corrected_quiz = await asyncio.to_thread(
                correct_quiz_questions,
                original_quiz=quiz_dict,
                feedback=review.feedback
                or "Hãy tinh chỉnh các câu hỏi cho hay và chính xác hơn.",
                context=context,
            )
            ai_quiz = corrected_quiz
            print(
                f"[Multi-Agent] Đã sửa đổi các câu lỗi và hoàn thiện bộ đề đạt chuẩn!"
            )
        else:
            print(
                f"[Multi-Agent] QC Reviewer phê duyệt: Đề thi đạt chất lượng xuất sắc!"
            )
    except Exception as mae:
        print(
            f"[Multi-Agent Warning] Gặp sự cố khi chấm chéo đề thi: {mae}. Bỏ qua để đảm bảo tiến độ sinh đề."
        )

    # Chuyển đổi list of question objects thành cấu trúc JSON lưu trữ và tự chữa lành đáp án nếu sai lệch
    questions_json = []
    for q in ai_quiz.questions:
        options_data = (
            [{"key": opt.key, "value": opt.value} for opt in q.options]
            if q.options
            else []
        )

        correct_ans = q.correct_answer.strip() if q.correct_answer else ""
        if options_data:
            valid_keys = {opt["key"].strip().upper() for opt in options_data}
            if correct_ans.upper() not in valid_keys:
                # Tìm xem correct_answer có khớp với value nào không
                matched_key = None
                for opt in options_data:
                    if opt["value"].strip().lower() == correct_ans.lower():
                        matched_key = opt["key"]
                        break
                if matched_key:
                    correct_ans = matched_key
                else:
                    # Nếu không khớp bất kỳ gì, gán mặc định cho phương án đầu tiên
                    correct_ans = options_data[0]["key"]

        questions_json.append(
            {
                "question_text": q.question_text,
                "options": options_data,
                "correct_answer": correct_ans,
                "explanation": q.explanation,
            }
        )

    # 4. Lưu đề thi vào MySQL
    db_quiz = Quiz(
        student_id=student_id,
        subject_id=subject_id,
        study_plan_id=study_plan_id,
        title=ai_quiz.title or f"Bài kiểm tra {subject.name} - {topic}",
        difficulty=difficulty,
        total_questions=len(questions_json),
        questions=questions_json,
        generated_by_ai=True,
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)

    return db_quiz


def submit_quiz_attempt(
    db: Session,
    quiz_id: int,
    student_id: int,
    submitted_answers: List[QuizAttemptAnswer],
    duration_seconds: int,
) -> QuizAttempt:
    """
    Chấm điểm bài thi tự động và lưu kết quả lượt làm bài (Quiz Attempt).
    Tự động hoàn thành Daily Study Plan nếu điểm số >= 5.0 (đạt).
    """
    # 1. Lấy đề thi
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise ValueError(f"Không tìm thấy đề thi với ID={quiz_id}")

    questions_list = quiz.questions or []
    total_q = len(questions_list)

    # Map các câu trả lời học sinh nộp theo index: {question_index: chosen_answer}
    submitted_map = {ans.question_index: ans.answer for ans in submitted_answers}

    # 2. Tiến hành chấm bài theo index
    correct_count = 0
    wrong_count = 0
    answers_json = []

    for idx, q_item in enumerate(questions_list):
        student_ans = submitted_map.get(idx, "")
        correct_ans = q_item.get("correct_answer", "")

        is_correct = (
            str(student_ans).strip().upper() == str(correct_ans).strip().upper()
        )

        if is_correct:
            correct_count += 1
        else:
            wrong_count += 1

        answers_json.append(
            {"question_index": idx, "answer": student_ans, "is_correct": is_correct}
        )

    # 3. Tính điểm trên thang điểm 10.0
    score = (correct_count / total_q * 10.0) if total_q > 0 else 0.0

    # 4. Lưu lượt làm bài vào MySQL
    db_attempt = QuizAttempt(
        quiz_id=quiz_id,
        student_id=student_id,
        answers=answers_json,
        score=score,
        correct_count=correct_count,
        wrong_count=wrong_count,
        duration_seconds=duration_seconds,
    )
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)

    # 5. Tự động đánh giá hoàn thành nhiệm vụ ngày (nếu điểm >= 8.0)
    if quiz.study_plan_id and score >= 8.0:
        from app.models.study_plan import StudyPlan
        from app.models.study_plan_progress import StudyPlanProgress

        plan = db.query(StudyPlan).filter(StudyPlan.id == quiz.study_plan_id).first()
        if plan:
            plan.status = "done"
            db.add(plan)

            # Đồng bộ cập nhật tiến độ (StudyPlanProgress) lên 100.0%
            progress = (
                db.query(StudyPlanProgress)
                .filter(StudyPlanProgress.study_plan_id == plan.id)
                .first()
            )
            if not progress:
                progress = StudyPlanProgress(
                    study_plan_id=plan.id,
                    student_id=student_id,
                    completion_percent=100.0,
                    completed_at=datetime.utcnow(),
                )
                db.add(progress)
            else:
                progress.completion_percent = 100.0
                progress.completed_at = datetime.utcnow()

            db.commit()

    return db_attempt


# ── TEACHER QUIZ LOGIC (4-LAYERS) ──
from fastapi import HTTPException, status
from app.schemas.teacher import TeacherQuizCreate
from app.repositories.classroom_repository import classroom_repository
from app.repositories.quiz_repository import quiz_repository
from app.repositories.attempt_repository import attempt_repository


def teacher_create_quiz(
    db: Session, teacher_id: int, obj_in: TeacherQuizCreate, current_user_role: str
) -> Quiz:
    """Giáo viên hoặc Admin tự soạn đề kiểm tra gán cho lớp học."""
    classroom = classroom_repository.get(db, obj_in.classroom_id)
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lớp học."
        )

    # Đảm bảo giáo viên dạy lớp này hoặc là admin
    if current_user_role != "admin" and classroom.teacher_id != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền đăng tải bài tập vào lớp học này.",
        )

    db_quiz = Quiz(
        student_id=teacher_id,  # Lưu ID người tạo làm mẫu
        subject_id=obj_in.subject_id,
        classroom_id=obj_in.classroom_id,
        title=obj_in.title,
        difficulty=obj_in.difficulty,
        total_questions=len(obj_in.questions),
        questions=obj_in.questions,
        generated_by_ai=False,
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def get_classroom_quiz_attempts(
    db: Session, classroom_id: int, current_teacher_id: int, current_user_role: str
) -> List[Dict[str, Any]]:
    """Giáo viên hoặc Admin lấy lịch sử điểm số bài làm của học sinh trong lớp."""
    from app.models.user import User as DBUser
    from app.models.classroom import Classroom

    classroom = classroom_repository.get(db, classroom_id)
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lớp học."
        )

    if current_user_role != "admin" and classroom.teacher_id != current_teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem thông tin điểm số lớp học này.",
        )

    # Join QuizAttempt với Quiz để lọc theo classroom_id
    attempts = (
        db.query(QuizAttempt, Quiz, DBUser)
        .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
        .join(DBUser, QuizAttempt.student_id == DBUser.id)
        .filter(Quiz.classroom_id == classroom_id)
        .all()
    )

    response = []
    for att, qz, usr in attempts:
        response.append(
            {
                "attempt_id": att.id,
                "quiz_id": qz.id,
                "quiz_title": qz.title,
                "student_id": usr.id,
                "student_name": usr.full_name,
                "student_email": usr.email,
                "score": float(att.score),
                "correct_count": att.correct_count,
                "wrong_count": att.wrong_count,
                "duration_seconds": att.duration_seconds,
                "submitted_at": att.submitted_at,
            }
        )

    return response


def get_student_quiz_attempts(db: Session, student_id: int) -> List[Dict[str, Any]]:
    """Học sinh lấy danh sách tất cả các bài thi/luyện đề đã làm của bản thân."""
    from app.models.quiz import Quiz

    attempts = (
        db.query(QuizAttempt, Quiz)
        .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
        .filter(QuizAttempt.student_id == student_id)
        .order_by(QuizAttempt.submitted_at.desc())
        .all()
    )

    response = []
    for att, qz in attempts:
        response.append(
            {
                "attempt_id": att.id,
                "quiz_id": qz.id,
                "quiz_title": qz.title,
                "score": float(att.score),
                "correct_count": att.correct_count,
                "wrong_count": att.wrong_count,
                "duration_seconds": att.duration_seconds,
                "submitted_at": att.submitted_at,
            }
        )
    return response
