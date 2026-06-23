import sys
import os
import asyncio

# Thêm Backend vào sys.path để import được app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Đọc file .env thủ công để thiết lập biến môi trường (chỉ set nếu chưa tồn tại)
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and "=" in line_str:
                key, val = line_str.split("=", 1)
                key_clean = key.strip()
                val_clean = val.strip()
                if key_clean not in os.environ or not os.environ[key_clean].strip():
                    os.environ[key_clean] = val_clean

from sqlalchemy.orm import Session
from app.database.mysql import SessionLocal
from app.database.mongodb import get_mongodb_db
from app.models.user import User
from app.models.subject import Subject
from app.models.classroom import Classroom
from app.models.question_bank import QuestionBank
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.quiz_attempt import QuizAttempt
from app.schemas.quiz_attempt import QuizAttemptAnswer
from app.services.embedding_service import vector_search_materials
from app.services.quiz_service import generate_and_save_quiz, submit_quiz_attempt


async def run_rag_quiz_test():
    print("=== BẮT ĐẦU CHẠY THỬ NGHIỆM TÍCH HỢP RAG QUIZ (GIAI ĐOẠN 3) ===")
    
    db: Session = SessionLocal()
    db_mongo = get_mongodb_db()
    
    try:
        # 1. Tìm thông tin seed
        student = db.query(User).filter(User.email == "student@test.com").first()
        teacher = db.query(User).filter(User.email == "teacher@test.com").first()
        subj = db.query(Subject).filter(Subject.code == "TRIETHOC").first()
        classroom = db.query(Classroom).filter(Classroom.class_code == "CLASS_TRIETHOC").first()
        
        if not all([student, teacher, subj, classroom]):
            print("❌ Lỗi: Vui lòng chạy scratch/seed_data.py trước để nạp dữ liệu mẫu!")
            return
            
        print(f"Học sinh: {student.full_name} (ID: {student.id})")
        print(f"Giáo viên: {teacher.full_name} (ID: {teacher.id})")
        print(f"Môn học: {subj.name} (ID: {subj.id})")
        print(f"Lớp học: {classroom.class_name} (ID: {classroom.id})")
        
        # 2. Kiểm tra Vector Search
        print("\nStep 2: Đang chạy thử nghiệm Vector Search trong MongoDB...")
        query_topic = "vật chất quyết định ý thức thế nào"
        results = await vector_search_materials(
            db_mongo=db_mongo,
            query_text=query_topic,
            subject_id=subj.id,
            top_k=1
        )
        if not results:
            print("❌ Không tìm thấy tài liệu liên quan trong MongoDB!")
            return
            
        print(f"  -> Tài liệu liên quan nhất tìm thấy:")
        print(f"     Chủ đề: {results[0]['topic']}")
        print(f"     Nội dung: {results[0]['content']}")
        print(f"     Độ tương đồng Cosine: {results[0]['score']:.4f}")
        
        # 3. Sinh đề thi bằng RAG + AI
        print("\nStep 3: Đang gọi AI Agent sinh đề thi RAG và lưu vào MySQL...")
        quiz = await generate_and_save_quiz(
            db=db,
            db_mongo=db_mongo,
            classroom_id=classroom.id,
            subject_id=subj.id,
            topic="Vật chất và ý thức",
            difficulty="easy",
            total_questions=2,
            question_type="mcq",
            teacher_id=teacher.id
        )
        
        print(f"  -> Sinh đề thi thành công!")
        print(f"     Tiêu đề đề thi: {quiz.title}")
        print(f"     Độ khó: {quiz.difficulty}")
        print(f"     Tổng số câu hỏi: {quiz.total_questions}")
        
        # In các câu hỏi để kiểm chứng
        print("\nChi tiết các câu hỏi trong đề:")
        # Lấy lại đầy đủ thông tin câu hỏi
        questions_junction = db.query(Question).filter(Question.quiz_id == quiz.id).all()
        
        simulated_answers = []
        for i, q_j in enumerate(questions_junction, 1):
            qb_item = q_j.question_bank_item
            print(f"  Câu {i}: {qb_item.question_text}")
            print(f"          Lựa chọn:")
            for opt in qb_item.options:
                print(f"             - {opt['key']}: {opt['value']}")
            print(f"          Đáp án đúng: {qb_item.correct_answer}")
            print(f"          Giải thích: {qb_item.explanation}")
            print("-" * 50)
            
            # Lưu đáp án mô phỏng: chọn đúng 1 câu, chọn sai 1 câu (nếu có 2 câu)
            # Giả định chọn đúng câu đầu tiên, chọn sai câu thứ hai
            selected_ans = qb_item.correct_answer if i == 1 else "Z" # 'Z' chắc chắn sai
            simulated_answers.append(
                QuizAttemptAnswer(
                    question_bank_id=qb_item.id,
                    answer=selected_ans
                )
            )

        # 4. Mô phỏng nộp bài thi
        print("\nStep 4: Mô phỏng học sinh nộp bài thi và chấm điểm...")
        attempt = submit_quiz_attempt(
            db=db,
            quiz_id=quiz.id,
            student_id=student.id,
            submitted_answers=simulated_answers,
            duration_seconds=120
        )
        
        print(f"  -> Nộp bài thành công!")
        print(f"     ID lượt làm bài: {attempt.id}")
        print(f"     Điểm số đạt được: {float(attempt.score):.2f}/10.0")
        print(f"     Số câu đúng: {attempt.correct_count}")
        print(f"     Số câu sai: {attempt.wrong_count}")
        print(f"     Thời gian làm: {attempt.duration_seconds} giây")
        print(f"     Chi tiết đáp án lưu trong MySQL: {attempt.answers}")

        print("\n=======================================================")
        print("     🎉 KIỂM THỬ TÍCH HỢP RAG QUIZ THÀNH CÔNG RỰC RỠ!   ")
        print("=======================================================")
        
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình chạy test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(run_rag_quiz_test())
