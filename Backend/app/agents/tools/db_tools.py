from sqlalchemy.orm import Session
from app.database.mysql import SessionLocal
from app.models.study_plan import StudyPlan
from app.models.learning_analytic import LearningAnalytic
from app.models.quiz_attempt import QuizAttempt
from app.models.subject import Subject

def get_student_study_plans_db(student_id: int) -> list:
    """
    Truy vấn danh sách kế hoạch học tập (Study Plans) của học sinh từ MySQL.
    """
    db: Session = SessionLocal()
    try:
        plans = db.query(StudyPlan).filter(StudyPlan.student_id == student_id).order_by(StudyPlan.study_date.asc(), StudyPlan.start_time.asc()).all()
        result = []
        for p in plans:
            result.append({
                "id": p.id,
                "title": p.title,
                "description": p.task_description,
                "date": p.study_date.strftime("%Y-%m-%d"),
                "time": f"{p.start_time.strftime('%H:%M:%S')} - {p.end_time.strftime('%H:%M:%S')}",
                "status": p.status,
                "ai_generated": p.ai_generated
            })
        return result
    finally:
        db.close()

def get_student_analytics_db(student_id: int, subject_id: int = None) -> dict:
    """
    Truy vấn bảng phân tích học lực (Learning Analytics) của học sinh từ MySQL.
    """
    db: Session = SessionLocal()
    try:
        query = db.query(LearningAnalytic).filter(LearningAnalytic.student_id == student_id)
        if subject_id:
            query = query.filter(LearningAnalytic.subject_id == subject_id)
        analytic = query.first()
        
        if not analytic:
            return {
                "average_score": 0.0,
                "quizzes_completed": 0,
                "weak_topics": [],
                "strong_topics": [],
                "ai_feedback": "Chưa có phân tích học lực cho học sinh này."
            }
            
        return {
            "average_score": float(analytic.average_score),
            "quizzes_completed": analytic.quizzes_completed,
            "weak_topics": analytic.weak_topics or [],
            "strong_topics": analytic.strong_topics or [],
            "ai_feedback": analytic.ai_feedback
        }
    finally:
        db.close()

def get_recent_attempts_db(student_id: int, limit: int = 5) -> list:
    """
    Truy vấn lịch sử các bài làm quiz gần nhất của học sinh từ MySQL.
    """
    db: Session = SessionLocal()
    try:
        attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).order_by(QuizAttempt.submitted_at.desc()).limit(limit).all()
        result = []
        for att in attempts:
            result.append({
                "quiz_id": att.quiz_id,
                "quiz_title": att.quiz.title if att.quiz else "Đề thi không tên",
                "score": float(att.score),
                "correct_count": att.correct_count,
                "wrong_count": att.wrong_count,
                "duration_seconds": att.duration_seconds,
                "submitted_at": att.submitted_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        return result
    finally:
        db.close()

def get_last_attempt_details_db(student_id: int) -> dict:
    """
    Truy vấn thông tin chi tiết bài làm quiz gần nhất của học sinh (bao gồm đáp án đã chọn, đáp án đúng, giải thích).
    """
    db: Session = SessionLocal()
    try:
        # Lấy quiz attempt gần nhất của học sinh
        att = db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).order_by(QuizAttempt.submitted_at.desc()).first()
        if not att:
            return {}
        
        quiz = att.quiz
        if not quiz:
            return {}

        # Tạo mapping đáp án học sinh chọn: {question_index: chosen_answer}
        chosen_map = {}
        if isinstance(att.answers, list):
            for ans in att.answers:
                q_idx = ans.get("question_index")
                chosen_map[q_idx] = ans.get("answer")

        # Lấy danh sách câu hỏi từ quiz.questions (JSON)
        questions_details = []
        questions_list = quiz.questions or []
        for idx, qb_item in enumerate(questions_list):
            chosen = chosen_map.get(idx, "Không có câu trả lời")
            correct = qb_item.get("correct_answer", "")
            is_correct = str(chosen).strip().lower() == str(correct).strip().lower()

            questions_details.append({
                "question_index": idx,
                "question_text": qb_item.get("question_text", ""),
                "options": qb_item.get("options", []),
                "correct_answer": correct,
                "chosen_answer": chosen,
                "is_correct": is_correct,
                "explanation": qb_item.get("explanation", "")
            })

        return {
            "quiz_title": quiz.title,
            "score": float(att.score),
            "correct_count": att.correct_count,
            "wrong_count": att.wrong_count,
            "submitted_at": att.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
            "questions": questions_details
        }
    finally:
        db.close()

