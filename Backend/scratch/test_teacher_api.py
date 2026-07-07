import requests
from app.database.mysql import SessionLocal
from app.models.user import User
from app.core.security import hash_password

BASE_URL = "http://localhost:8000/api/v1"


def setup_users():
    print("--- KHỞI TẠO TÀI KHOẢN TEST TRONG DATABASE ---")
    db = SessionLocal()
    try:
        # 1. Tạo tài khoản Giáo viên
        teacher = db.query(User).filter(User.email == "teacher@edumind.com").first()
        if not teacher:
            teacher = User(
                email="teacher@edumind.com",
                password_hash=hash_password("teacherpassword"),
                full_name="Giáo viên Hoa",
                role="teacher",
                is_active=True,
            )
            db.add(teacher)
            print("Đã tạo Giáo viên test: teacher@edumind.com")
        else:
            teacher.role = "teacher"
            teacher.is_active = True
            print("Đã xác minh Giáo viên test.")

        # 2. Tạo tài khoản Học sinh
        student = (
            db.query(User).filter(User.email == "student_test@edumind.com").first()
        )
        if not student:
            student = User(
                email="student_test@edumind.com",
                password_hash=hash_password("studentpassword"),
                full_name="Học sinh Bình",
                role="student",
                is_active=True,
            )
            db.add(student)
            print("Đã tạo Học sinh test: student_test@edumind.com")
        else:
            student.role = "student"
            student.is_active = True
            print("Đã xác minh Học sinh test.")

        db.commit()
    finally:
        db.close()


def run_integration_test():
    setup_users()

    # ── ĐĂNG NHẬP GIÁO VIÊN ──
    print("\n--- 1. ĐĂNG NHẬP TÀI KHOẢN GIÁO VIÊN ---")
    res = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "teacher@edumind.com", "password": "teacherpassword"},
    )
    assert res.status_code == 200, f"Đăng nhập GV lỗi: {res.text}"
    teacher_token = res.json()["access_token"]
    t_headers = {"Authorization": f"Bearer {teacher_token}"}
    print("Giáo viên đăng nhập thành công!")

    # ── TẠO MÔN HỌC ──
    print("\n--- 2. GIÁO VIÊN TẠO MÔN HỌC MỚI ---")
    import random

    subject_code = f"TEST{random.randint(100,999)}"
    subj_payload = {
        "name": "Môn kiểm thử tự động",
        "code": subject_code,
        "description": "Mô tả môn học test",
    }
    res = requests.post(f"{BASE_URL}/subjects/", json=subj_payload, headers=t_headers)
    assert res.status_code == 201, f"Tạo môn học lỗi: {res.text}"
    subject_id = res.json()["id"]
    print(f"Tạo thành công môn học ID: {subject_id} (Mã: {subject_code})")

    # ── TẠO LỚP HỌC ──
    print("\n--- 3. GIÁO VIÊN MỞ LỚP HỌC MỚI ---")
    class_code = f"CLASS-{subject_code}"
    class_payload = {
        "subject_id": subject_id,
        "class_name": "Lớp học kiểm thử 10A",
        "class_code": class_code,
        "description": "Lớp học dành cho kiểm thử tự động",
    }
    res = requests.post(
        f"{BASE_URL}/classrooms/", json=class_payload, headers=t_headers
    )
    assert res.status_code == 201, f"Tạo lớp lỗi: {res.text}"
    classroom_id = res.json()["id"]
    print(f"Tạo thành công lớp học ID: {classroom_id} (Mã lớp: {class_code})")

    # ── THÊM HỌC SINH VÀO LỚP ──
    print("\n--- 4. THÊM HỌC SINH VÀO LỚP HỌC ---")
    add_student_payload = {"student_email": "student_test@edumind.com"}
    res = requests.post(
        f"{BASE_URL}/classrooms/{classroom_id}/students",
        json=add_student_payload,
        headers=t_headers,
    )
    assert res.status_code == 200, f"Thêm học sinh lỗi: {res.text}"
    print("Đã thêm học sinh student_test@edumind.com vào lớp thành công.")

    # ── XEM TIẾN ĐỘ LỚP ──
    print("\n--- 5. GIÁO VIÊN KIỂM TRA TIẾN ĐỘ TIẾN TRÌNH LỚP HỌC ---")
    res = requests.get(
        f"{BASE_URL}/classrooms/{classroom_id}/students/progress", headers=t_headers
    )
    assert res.status_code == 200, f"Lấy tiến độ lớp học lỗi: {res.text}"
    print("Lấy danh sách tiến độ lớp học thành công:")
    print(res.json())

    # ── TẢI TÀI LIỆU LÊN ──
    print("\n--- 6. GIÁO VIÊN ĐĂNG TẢI TÀI LIỆU HỌC TẬP MỚI ---")
    files = {
        "file": (
            "on_tap_toan.txt",
            "Noi dung tai lieu on tap toan dai so...",
            "text/plain",
        )
    }
    data = {"subject_id": subject_id, "title": "Tài liệu ôn tập Toán Đại số chương 1"}
    res = requests.post(
        f"{BASE_URL}/documents/", data=data, files=files, headers=t_headers
    )
    assert res.status_code == 201, f"Đăng tài liệu lỗi: {res.text}"
    doc_id = res.json()["id"]
    print(f"Đăng tải tài liệu thành công! ID: {doc_id}")

    # ── GIÁO VIÊN TẠO ĐỀ BÀI TẬP (QUIZ) ──
    print("\n--- 7. GIÁO VIÊN SOẠN BÀI TẬP TỰ LUYỆN CHO LỚP HỌC ---")
    quiz_payload = {
        "title": "Bài tập kiểm tra 15 phút Toán",
        "difficulty": "medium",
        "subject_id": subject_id,
        "classroom_id": classroom_id,
        "questions": [
            {
                "question_text": "Căn bậc hai của 16 là bao nhiêu?",
                "options": [
                    {"key": "A", "value": "2"},
                    {"key": "B", "value": "4"},
                    {"key": "C", "value": "8"},
                    {"key": "D", "value": "16"},
                ],
                "correct_answer": "B",
                "explanation": "Vì 4 x 4 = 16",
            }
        ],
    }
    res = requests.post(
        f"{BASE_URL}/quizzes/teacher/create", json=quiz_payload, headers=t_headers
    )
    assert res.status_code == 201, f"Tạo đề kiểm tra lỗi: {res.text}"
    quiz_id = res.json()["id"]
    print(f"Đã đăng đề kiểm tra thành công! ID: {quiz_id}")

    # ── ĐĂNG NHẬP HỌC SINH & LÀM BÀI ──
    print("\n--- 8. HỌC SINH ĐĂNG NHẬP VÀ NỘP BÀI THI ---")
    res = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "student_test@edumind.com", "password": "studentpassword"},
    )
    assert res.status_code == 200, f"Đăng nhập HS lỗi: {res.text}"
    student_token = res.json()["access_token"]
    s_headers = {"Authorization": f"Bearer {student_token}"}

    submit_payload = {
        "answers": [{"question_index": 0, "answer": "B", "is_correct": True}],
        "duration_seconds": 45,
    }
    res = requests.post(
        f"{BASE_URL}/quizzes/{quiz_id}/submit", json=submit_payload, headers=s_headers
    )
    assert res.status_code == 200, f"HS nộp bài lỗi: {res.text}"
    print(f"Học sinh nộp bài thi thành công! Điểm đạt được: {res.json()['score']}")

    # ── GIÁO VIÊN XEM BÁO CÁO NỘP BÀI ──
    print("\n--- 9. GIÁO VIÊN KIỂM TRA LỊCH SỬ ĐIỂM SỐ LỚP HỌC ---")
    res = requests.get(
        f"{BASE_URL}/quizzes/classroom/{classroom_id}/attempts", headers=t_headers
    )
    assert res.status_code == 200, f"GV xem điểm lỗi: {res.text}"
    print("Thông tin làm bài của học sinh nhận được:")
    import json

    print(json.dumps(res.json(), indent=2, ensure_ascii=False))

    print(
        "\n>>> TẤT CẢ CÁC BƯỚC KIỂM THỬ TÍCH HỢP CHO GIÁO VIÊN ĐÃ THÀNH CÔNG 100%! <<<"
    )


if __name__ == "__main__":
    run_integration_test()
