import sys
import os
from datetime import date, datetime

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
from app.models.user import User
from app.models.subject import Subject
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.notification import Notification
from app.models.ai_recommendation_review import AIRecommendationReview
from app.schemas.classroom import ClassroomCreate
from app.services.classroom_service import (
    create_classroom,
    add_student_to_classroom,
    add_subject_to_classroom,
    get_classroom_detail,
)
from app.services.recommendation_service import (
    get_pending_reviews,
    review_recommendation,
)


def run_teacher_flow_test():
    print("=== BẮT ĐẦU CHẠY THỬ NGHIỆM TÍCH HỢP 4 TẦNG (APIS GIÁO VIÊN) ===")

    db: Session = SessionLocal()

    try:
        # 1. Lấy thông tin người dùng mẫu
        teacher = db.query(User).filter(User.email == "teacher@test.com").first()
        student = db.query(User).filter(User.email == "student@test.com").first()
        subj = db.query(Subject).filter(Subject.code == "TRIETHOC").first()

        if not all([teacher, student, subj]):
            print(
                "❌ Lỗi: Vui lòng chạy scratch/seed_data.py trước để nạp dữ liệu mẫu!"
            )
            return

        print(f"Giáo viên: {teacher.full_name} (ID: {teacher.id})")
        print(f"Học sinh: {student.full_name} (ID: {student.id})")
        print(f"Môn học: {subj.name} (ID: {subj.id})")

        # 2. Tạo lớp học mới bằng Service
        print("\nStep 2: Đang tạo lớp học mới...")
        class_code = "TOAN101_TEST"
        # Xóa lớp học cũ nếu trùng mã để test chạy lặp lại được
        from app.models.classroom import Classroom

        db.query(Classroom).filter(Classroom.class_code == class_code).delete()
        db.commit()

        classroom_in = ClassroomCreate(
            class_name="Lớp học Toán Cao Cấp",
            class_code=class_code,
            description="Lớp học kiểm thử tự động cho giáo viên",
        )
        classroom = create_classroom(db=db, teacher_id=teacher.id, obj_in=classroom_in)
        print(
            f"  -> Tạo lớp học thành công! ID: {classroom.id}, Code: {classroom.class_code}"
        )

        # 3. Gán môn học và học sinh vào lớp bằng Service
        print("\nStep 3: Gán môn học và học sinh vào lớp...")
        add_subject_to_classroom(
            db=db, classroom_id=classroom.id, teacher_id=teacher.id, subject_id=subj.id
        )
        add_student_to_classroom(
            db=db,
            classroom_id=classroom.id,
            teacher_id=teacher.id,
            student_email=student.email,
        )
        print("  -> Gán môn học và học sinh thành công!")

        # 4. Truy vấn chi tiết lớp học
        print("\nStep 4: Kiểm tra chi tiết lớp học...")
        detail = get_classroom_detail(db=db, classroom_id=classroom.id, user=teacher)
        print(f"  -> Lớp học: {detail['classroom'].class_name}")
        print(f"     Môn học gán kèm: {[s.name for s in detail['subjects']]}")
        print(f"     Học sinh tham gia: {[st.full_name for st in detail['students']]}")

        assert len(detail["subjects"]) == 1
        assert len(detail["students"]) == 1

        # 5. Tạo mục tiêu giả lập cho học sinh để chuẩn bị test sync StudyPlan
        print("\nStep 5: Chuẩn bị mục tiêu học tập mẫu cho học sinh...")
        # Xoá các goal và plan cũ của học sinh này
        db.query(StudyPlan).filter(StudyPlan.student_id == student.id).delete()
        db.query(StudyGoal).filter(StudyGoal.student_id == student.id).delete()
        db.commit()

        goal = StudyGoal(
            student_id=student.id,
            subject_id=subj.id,
            title="Đạt 9.0 môn Triết học",
            target_score=9.0,
            deadline=date.today(),
            status="active",
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        print(f"  -> Tạo mục tiêu ID: {goal.id} cho học sinh thành công.")

        # 6. Tạo đề xuất ôn tập AI giả lập ở trạng thái pending
        print("\nStep 6: Đang tạo đề xuất ôn tập AI (pending)...")
        # Xoá các review cũ để tránh rác dữ liệu
        db.query(AIRecommendationReview).filter(
            AIRecommendationReview.student_id == student.id
        ).delete()
        db.commit()

        ai_review = AIRecommendationReview(
            student_id=student.id,
            recommendation="AI khuyên bạn: Ôn tập lại phần Vật chất và Ý thức do điểm Quiz thấp.",
            status="pending",
        )
        db.add(ai_review)
        db.commit()
        db.refresh(ai_review)
        print(f"  -> Tạo đề xuất AI thành công, ID: {ai_review.id}")

        # 7. Giáo viên truy vấn danh sách đề xuất cần duyệt
        print("\nStep 7: Giáo viên truy vấn danh sách đề xuất pending...")
        pending_reviews = get_pending_reviews(db=db, teacher_id=teacher.id)
        print(f"  -> Số đề xuất đang chờ duyệt: {len(pending_reviews)}")
        assert len(pending_reviews) == 1
        print(f"     Nội dung đề xuất: '{pending_reviews[0].recommendation}'")

        # 8. Giáo viên phê duyệt đề xuất (approved) -> Xem có tự động đồng bộ StudyPlan và Notification không
        print("\nStep 8: Giáo viên phê duyệt đề xuất (Approved)...")
        reviewed = review_recommendation(
            db=db,
            review_id=ai_review.id,
            teacher_id=teacher.id,
            status="approved",
            teacher_feedback="Rất chuẩn, duyệt bài học bổ sung này cho học sinh.",
        )
        print(f"  -> Duyệt thành công! Trạng thái: {reviewed.status}")

        # 9. Xác minh dữ liệu sinh tự động
        print("\nStep 9: Kiểm tra đồng bộ dữ liệu sau khi duyệt...")
        # Lấy lịch học (StudyPlan)
        plans = db.query(StudyPlan).filter(StudyPlan.student_id == student.id).all()
        print(f"  -> Lịch học tự động sinh thêm: {len(plans)} nhiệm vụ")
        for p in plans:
            print(
                f"     Nhiệm vụ: {p.title} (Ngày: {p.study_date}, Thời gian: {p.start_time}-{p.end_time})"
            )
            print(f"     Chi tiết: {p.task_description}")
        assert len(plans) == 1

        # Lấy thông báo (Notification)
        notifications = (
            db.query(Notification).filter(Notification.user_id == student.id).all()
        )
        print(f"  -> Thông báo gửi học sinh: {len(notifications)} tin nhắn")
        for n in notifications:
            print(f"     Tiêu đề: {n.title} | Nội dung: {n.content}")
        assert len(notifications) == 1

        print("\n=======================================================")
        print("     🎉 KIỂM THỬ TÍCH HỢP 4 TẦNG APIS GIÁO VIÊN THÀNH CÔNG!   ")
        print("=======================================================")

    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình chạy test: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    run_teacher_flow_test()
