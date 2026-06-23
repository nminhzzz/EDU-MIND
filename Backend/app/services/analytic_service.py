"""
Service xử lý các nghiệp vụ đánh giá học lực (Learning Analytics)
và tự động sinh đề xuất học tập AI (Recommendation Reviews) — Giai đoạn 4.
"""
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from typing import Optional

from app.models.subject import Subject
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.learning_analytic import LearningAnalytic
from app.models.ai_recommendation_review import AIRecommendationReview
from app.models.user import User
from app.models.notification import Notification

from app.agents.analytics_agent.agent import evaluate_learning_performance
from app.agents.recommender.agent import generate_recommendation


def update_student_analytics_and_recommend(
    db: Session,
    student_id: int,
    subject_id: int,
    quiz_id: int,
    score: float
):
    """
    Background Task:
    1. Cập nhật hồ sơ học tập (LearningAnalytic) và gọi AI đánh giá lại học lực.
    2. Nếu điểm thi dưới 8.0, tự động gọi AI sinh đề xuất ôn tập (chờ giáo viên duyệt).
    """
    # ── 1. Lấy thông tin môn học, học sinh & đề thi ──
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    student = db.query(User).filter(User.id == student_id).first()
    quiz = (
        db.query(Quiz)
        .options(joinedload(Quiz.classroom))
        .filter(Quiz.id == quiz_id)
        .first()
    )

    if not subject or not student or not quiz:
        return  # Bỏ qua nếu dữ liệu không nhất quán

    # ── 2. Lấy hoặc tạo bản ghi LearningAnalytic cho học sinh theo môn học này ──
    analytic = (
        db.query(LearningAnalytic)
        .filter(
            LearningAnalytic.student_id == student_id,
            LearningAnalytic.subject_id == subject_id
        )
        .first()
    )
    if not analytic:
        analytic = LearningAnalytic(
            student_id=student_id,
            subject_id=subject_id,
            average_score=0.0,
            quizzes_completed=0,
            weak_topics=[],
            strong_topics=[]
        )
        db.add(analytic)
        db.flush()

    # ── 3. Lấy toàn bộ lịch sử làm bài thi của học sinh cho môn học này ──
    attempts = (
        db.query(QuizAttempt)
        .join(Quiz, Quiz.id == QuizAttempt.quiz_id)
        .filter(
            QuizAttempt.student_id == student_id,
            Quiz.subject_id == subject_id
        )
        .all()
    )

    # ── 4. Tính toán lại số đề hoàn thành & điểm trung bình ──
    quizzes_completed = len(attempts)
    average_score = sum(float(a.score) for a in attempts) / quizzes_completed if quizzes_completed > 0 else 0.0

    analytic.quizzes_completed = quizzes_completed
    analytic.average_score = average_score

    # ── 5. Chuẩn bị lịch sử làm bài gửi AI đánh giá học lực ──
    attempts_history = []
    for a in attempts:
        # Tìm chủ đề đề thi
        a_quiz = db.query(Quiz).filter(Quiz.id == a.quiz_id).first()
        topic_name = a_quiz.title if a_quiz else f"Bài kiểm tra {subject.name}"
        attempts_history.append({
            "topic": topic_name,
            "score": float(a.score),
            "is_passed": float(a.score) >= 5.0
        })

    # ── 6. Gọi AI Analytics Agent đánh giá lại ──
    try:
        ai_evaluation = evaluate_learning_performance(
            subject_name=subject.name,
            attempts_history=attempts_history
        )
        # Chuyển đổi Pydantic schemas sang JSON dicts để lưu vào MySQL
        analytic.weak_topics = [t.model_dump() for t in ai_evaluation.weak_topics]
        analytic.strong_topics = [t.model_dump() for t in ai_evaluation.strong_topics]
        analytic.ai_feedback = ai_evaluation.ai_feedback
    except Exception as eval_err:
        # Nếu AI lỗi, ghi nhận log và giữ nguyên đánh giá cũ
        print(f"[Warning] AI Analytics Agent error: {eval_err}")

    # ── 7. Nếu bài thi vừa làm chưa đạt yêu cầu (< 8.0), tự sinh đề xuất ôn tập AI ──
    if score < 8.0:
        # Gọi AI Recommender Agent sinh đề xuất học tập cụ thể
        try:
            ai_recommendation_text = generate_recommendation(
                subject_name=subject.name,
                topic_name=quiz.title,
                score=score,
                weak_topics=analytic.weak_topics
            )

            # Giáo viên phụ trách lớp học (đề xuất sẽ gửi cho giáo viên này duyệt)
            teacher_id = quiz.classroom.teacher_id if (quiz.classroom and quiz.classroom.teacher_id) else None

            # Tạo bản ghi đề xuất ôn tập ở trạng thái pending (HITL)
            db_review = AIRecommendationReview(
                student_id=student_id,
                teacher_id=teacher_id,
                recommendation=ai_recommendation_text,
                status="pending"
            )
            db.add(db_review)

            # Gửi thông báo đến giáo viên nếu được gán
            if teacher_id:
                db_teacher_notif = Notification(
                    user_id=teacher_id,
                    title="Đề xuất ôn tập AI mới cần duyệt",
                    content=f"Học sinh {student.full_name} làm bài kiểm tra '{quiz.title}' đạt {score}/10. Có đề xuất ôn tập AI đang chờ duyệt.",
                    type="plan",
                    is_read=False
                )
                db.add(db_teacher_notif)

        except Exception as rec_err:
            print(f"[Warning] AI Recommender Agent error: {rec_err}")

    # ── 8. Adaptive Plan: Nếu học sinh có lộ trình active và điểm yếu, tự động refine ──
    try:
        from app.services.unified_service import get_active_goal_for_subject, generate_unified_draft
        from app.database.mongodb import get_mongodb_db
        from app.repositories import chat_repository

        active_goal = get_active_goal_for_subject(db, student_id, subject_id)
        if active_goal and analytic.weak_topics and len(analytic.weak_topics) > 0:
            weak_topics_str = "; ".join(
                [t.get("topic", str(t)) if isinstance(t, dict) else str(t) for t in analytic.weak_topics]
            ) if analytic.weak_topics else ""

            if weak_topics_str and score < 7.0:
                print(f"-> Adaptive Plan: Refining plan for student {student_id} due to weak topics: {weak_topics_str}")

                topic_chat_session = await chat_repository.create_chat_session(
                    student_id=student_id,
                    title=f"Tự động điều chỉnh lộ trình - {subject.name} (Điểm yếu)"
                )

                db_mongo = get_mongodb_db()
                if db_mongo is not None:
                    await chat_repository.add_chat_message(
                        topic_chat_session,
                        "user",
                        f"Tôi vừa làm bài '{quiz.title}' được {score}/10. "
                        f"Các phần yếu cần cải thiện: {weak_topics_str}. "
                        f"Hãy điều chỉnh lộ trình học tập của tôi để tập trung ôn các phần này."
                    )

                db_student_notif_adaptive = Notification(
                    user_id=student_id,
                    title="Lộ trình học được điều chỉnh tự động",
                    content=f"Dựa trên kết quả bài thi '{quiz.title}' ({score}/10), AI đã phân tích điểm yếu và điều chỉnh lộ trình học tập môn {subject.name}. Vui lòng kiểm tra lại lộ trình.",
                    type="plan",
                    is_read=False
                )
                db.add(db_student_notif_adaptive)
    except Exception as adaptive_err:
        print(f"[Warning] Adaptive Plan error: {adaptive_err}")

    # ── 9. Gửi thông báo kết quả cập nhật cho học sinh ──
    db_student_notif = Notification(
        user_id=student_id,
        title="Hồ sơ học tập được cập nhật",
        content=f"Kết quả bài thi '{quiz.title}' đạt {score}/10 đã được lưu và đánh giá vào profile học sinh môn {subject.name}.",
        type="score",
        is_read=False
    )
    db.add(db_student_notif)

    db.commit()
