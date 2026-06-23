import sys
import os
from datetime import datetime, date, timedelta, time

# Thêm Backend vào sys.path để import được app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Đọc file .env thủ công để thiết lập biến môi trường
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and "=" in line_str:
                key, val = line_str.split("=", 1)
                os.environ[key.strip()] = val.strip()

from sqlalchemy import create_engine
from app.database.mysql import engine, SessionLocal
from app.models.base import Base

# Import các models cần thiết
from app.models.user import User
from app.models.subject import Subject
from app.models.classroom import Classroom
from app.models.classroom_student import ClassroomStudent
from app.models.classroom_subject import ClassroomSubject
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.question_bank import QuestionBank
from app.models.quiz_attempt import QuizAttempt
from app.models.learning_analytic import LearningAnalytic
from app.models.ai_recommendation_review import AIRecommendationReview
from app.models.notification import Notification

import app.services.quiz_service as quiz_service
import app.services.analytic_service as analytic_service

def run_evaluation_test():
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your_gemini_api_key_here" or gemini_key.strip() == "":
        print("WARNING: Bạn chưa điền GEMINI_API_KEY thực tế vào file .env!")
        return

    print("--- KHỞI CHẠY KIỂM THỬ LUỒNG ĐÁNH GIÁ HỌC LỰC & ĐỀ XUẤT AI ---")
    
    db = SessionLocal()
    try:
        # 1. Lấy hoặc tạo dữ liệu Học sinh, Giáo viên, Môn học, Lớp học
        student = db.query(User).filter(User.email == "student_test_eval@test.com").first()
        if not student:
            student = User(
                email="student_test_eval@test.com",
                password_hash="mockpassword",
                full_name="Nguyễn Văn Học Sinh (Test Eval)",
                role="student",
                grade="Đại học năm 1",
                learning_level="average"
            )
            db.add(student)
            db.commit()
            db.refresh(student)

        teacher = db.query(User).filter(User.email == "teacher_test_eval@test.com").first()
        if not teacher:
            teacher = User(
                email="teacher_test_eval@test.com",
                password_hash="mockpassword",
                full_name="Thầy Cô Giáo Viên (Test Eval)",
                role="teacher",
                grade="Đại học"
            )
            db.add(teacher)
            db.commit()
            db.refresh(teacher)

        subject = db.query(Subject).filter(Subject.code == "TRIETHOC_EVAL").first()
        if not subject:
            subject = Subject(
                name="Triết học Mác - Lênin (Kiểm thử)",
                code="TRIETHOC_EVAL",
                description="Môn học Triết học cơ bản phục vụ kiểm thử"
            )
            db.add(subject)
            db.commit()
            db.refresh(subject)

        classroom = db.query(Classroom).filter(Classroom.class_code == "CLASS_EVAL").first()
        if not classroom:
            classroom = Classroom(
                teacher_id=teacher.id,
                class_name="Lớp Triết học Eval",
                class_code="CLASS_EVAL",
                description="Lớp học kiểm thử tự đánh giá"
            )
            db.add(classroom)
            db.commit()
            db.refresh(classroom)

            # Gán môn học và học sinh vào lớp học
            class_subj = ClassroomSubject(classroom_id=classroom.id, subject_id=subject.id)
            class_student = ClassroomStudent(classroom_id=classroom.id, student_id=student.id)
            db.add(class_subj)
            db.add(class_student)
            db.commit()

        # 2. Tạo một Đề thi mẫu (Quiz) và 3 câu hỏi mẫu
        quiz = db.query(Quiz).filter(Quiz.classroom_id == classroom.id, Quiz.title == "Bài thi mẫu chủ đề Vật chất").first()
        if not quiz:
            quiz = Quiz(
                classroom_id=classroom.id,
                subject_id=subject.id,
                teacher_id=teacher.id,
                title="Bài thi mẫu chủ đề Vật chất",
                difficulty="medium",
                total_questions=3,
                generated_by_ai=True
            )
            db.add(quiz)
            db.commit()
            db.refresh(quiz)

            # Tạo 3 câu hỏi trong QuestionBank
            q1 = QuestionBank(
                subject_id=subject.id,
                topic="Vật chất và ý thức",
                difficulty="medium",
                question_text="Theo triết học Mác - Lênin, vật chất là gì?",
                options=[{"key": "A", "value": "Thực tại khách quan"}, {"key": "B", "value": "Ý thức chủ quan"}],
                correct_answer="A",
                explanation="Vật chất là thực tại khách quan tồn tại độc lập với cảm giác con người."
            )
            q2 = QuestionBank(
                subject_id=subject.id,
                topic="Vật chất và ý thức",
                difficulty="medium",
                question_text="Ý thức phản ánh cái gì?",
                options=[{"key": "A", "value": "Thế giới khách quan"}, {"key": "B", "value": "Ý muốn của thần linh"}],
                correct_answer="A",
                explanation="Ý thức phản ánh năng động thế giới khách quan."
            )
            q3 = QuestionBank(
                subject_id=subject.id,
                topic="Vật chất và ý thức",
                difficulty="medium",
                question_text="Mối quan hệ giữa vật chất và ý thức?",
                options=[{"key": "A", "value": "Vật chất quyết định ý thức"}, {"key": "B", "value": "Ý thức quyết định vật chất"}],
                correct_answer="A",
                explanation="Vật chất có trước, quyết định ý thức; ý thức có tính độc lập tương đối."
            )
            db.add(q1)
            db.add(q2)
            db.add(q3)
            db.commit()
            db.refresh(q1)
            db.refresh(q2)
            db.refresh(q3)

            # Liên kết câu hỏi vào quiz
            j1 = Question(quiz_id=quiz.id, question_bank_id=q1.id)
            j2 = Question(quiz_id=quiz.id, question_bank_id=q2.id)
            j3 = Question(quiz_id=quiz.id, question_bank_id=q3.id)
            db.add(j1)
            db.add(j2)
            db.add(j3)
            db.commit()

            # Nạp lại câu hỏi để lát nữa tìm id
            questions_bank_list = [q1, q2, q3]
        else:
            # Nếu đã tồn tại đề thi, lấy danh sách câu hỏi
            questions_bank_list = (
                db.query(QuestionBank)
                .join(Question, Question.question_bank_id == QuestionBank.id)
                .filter(Question.quiz_id == quiz.id)
                .all()
            )

        print(f"Đã chuẩn bị đề thi: '{quiz.title}' có {len(questions_bank_list)} câu hỏi.")

        # 3. Học sinh nộp bài thi (giả lập trả lời sai 2 câu để được 3.33 điểm, chưa đạt yêu cầu)
        # Câu 1: trả lời A (Đúng)
        # Câu 2: trả lời B (Sai)
        # Câu 3: trả lời B (Sai)
        submitted_answers = [
            {"question_bank_id": questions_bank_list[0].id, "answer": "A"},
            {"question_bank_id": questions_bank_list[1].id, "answer": "B"},
            {"question_bank_id": questions_bank_list[2].id, "answer": "B"}
        ]
        
        from app.schemas.quiz_attempt import QuizAttemptAnswer
        answers_schemas = [QuizAttemptAnswer(**ans) for ans in submitted_answers]

        print("\nTiến hành chấm thi tự động...")
        attempt = quiz_service.submit_quiz_attempt(
            db=db,
            quiz_id=quiz.id,
            student_id=student.id,
            submitted_answers=answers_schemas,
            duration_seconds=120
        )
        print(f"  -> Kết quả: {attempt.correct_count} câu đúng | Score: {attempt.score}/10")

        # 4. Kích hoạt logic phân tích học lực và đề xuất học tập ôn luyện (đồng bộ để lấy kết quả)
        print("\nAI đang tiến hành phân tích học lực và lập đề xuất ôn tập (RAG)...")
        analytic_service.update_student_analytics_and_recommend(
            db=db,
            student_id=student.id,
            subject_id=subject.id,
            quiz_id=quiz.id,
            score=float(attempt.score)
        )

        # 5. Truy vấn dữ liệu thực tế từ MySQL để kiểm tra
        print("\n=======================================================")
        print("         🎉 KẾT QUẢ PHÂN TÍCH VÀ ĐỀ XUẤT AI            ")
        print("=======================================================")
        
        # Kiểm tra LearningAnalytics
        analytic = db.query(LearningAnalytic).filter(
            LearningAnalytic.student_id == student.id,
            LearningAnalytic.subject_id == subject.id
        ).first()
        
        print("\n1. Bảng learning_analytics (Hồ sơ học lực học sinh):")
        print(f"  - Số đề đã hoàn thành: {analytic.quizzes_completed}")
        print(f"  - Điểm số trung bình môn: {analytic.average_score:.2f}")
        print(f"  - Nhận xét chi tiết từ AI:\n    {analytic.ai_feedback}")
        print(f"  - Các chủ đề cần cải thiện (weak_topics): {analytic.weak_topics}")
        print(f"  - Các chủ đề nắm vững (strong_topics): {analytic.strong_topics}")

        # Kiểm tra AIRecommendationReview
        recommendations = db.query(AIRecommendationReview).filter(
            AIRecommendationReview.student_id == student.id
        ).all()
        print(f"\n2. Bảng ai_recommendation_reviews (Đề xuất ôn tập AI chờ giáo viên duyệt):")
        print(f"  - Tìm thấy: {len(recommendations)} đề xuất.")
        for i, rec in enumerate(recommendations, 1):
            print(f"  * Đề xuất {i}: [Trạng thái: {rec.status}] | Giáo viên phụ trách ID: {rec.teacher_id}")
            print(f"    Nội dung đề xuất từ AI:\n{rec.recommendation}")
            print("-" * 60)

        # Kiểm tra Notifications
        notifs = db.query(Notification).filter(Notification.user_id.in_([student.id, teacher.id])).all()
        print(f"\n3. Thông báo hệ thống (Notifications):")
        for n in notifs:
            user_role = "Học sinh" if n.user_id == student.id else "Giáo viên"
            print(f"  - [{user_role}] Tiêu đề: {n.title} | Nội dung: {n.content}")

    except Exception as e:
        print(f"\nERROR: Lỗi luồng đánh giá học lực: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_evaluation_test()
