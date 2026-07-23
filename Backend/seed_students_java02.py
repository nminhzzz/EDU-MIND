# -*- coding: utf-8 -*-
"""Seed 20 students into the java02 classroom (class_code=JAVAK05)."""

from app.database.mysql import SessionLocal
from app.models.user import User
from app.models.classroom import Classroom
from app.models.classroom_student import ClassroomStudent
from app.core.security import hash_password

STUDENTS = [
    {"email": "nguyenvana@edumind.vn",   "full_name": "Nguyễn Văn An"},
    {"email": "tranthib@edumind.vn",     "full_name": "Trần Thị Bích"},
    {"email": "levanc@edumind.vn",       "full_name": "Lê Văn Cường"},
    {"email": "phamthid@edumind.vn",     "full_name": "Phạm Thị Dung"},
    {"email": "hoangvane@edumind.vn",    "full_name": "Hoàng Văn Đức"},
    {"email": "vuthif@edumind.vn",       "full_name": "Vũ Thị Phương"},
    {"email": "dangvang@edumind.vn",     "full_name": "Đặng Văn Giang"},
    {"email": "buithih@edumind.vn",      "full_name": "Bùi Thị Hương"},
    {"email": "dovani@edumind.vn",       "full_name": "Đỗ Văn Khải"},
    {"email": "ngothik@edumind.vn",      "full_name": "Ngô Thị Kim"},
    {"email": "trinhvanl@edumind.vn",    "full_name": "Trịnh Văn Long"},
    {"email": "luuthim@edumind.vn",      "full_name": "Lưu Thị Mai"},
    {"email": "phanvann@edumind.vn",     "full_name": "Phan Văn Nam"},
    {"email": "dinhthio@edumind.vn",     "full_name": "Đinh Thị Oanh"},
    {"email": "lyvanp@edumind.vn",       "full_name": "Lý Văn Phúc"},
    {"email": "hathiq@edumind.vn",       "full_name": "Hà Thị Quỳnh"},
    {"email": "maidangr@edumind.vn",     "full_name": "Mai Đăng Rạng"},
    {"email": "caothis@edumind.vn",      "full_name": "Cao Thị Sen"},
    {"email": "truongvant@edumind.vn",   "full_name": "Trương Văn Tài"},
    {"email": "lamthiu@edumind.vn",      "full_name": "Lâm Thị Uyên"},
]

PASSWORD = "student123"


def main():
    db = SessionLocal()
    try:
        # Find the java02 classroom
        classroom = db.query(Classroom).filter(Classroom.class_code == "JAVAK05").first()
        if not classroom:
            print("❌ Không tìm thấy lớp JAVAK05 (java02)!")
            return

        print(f"✔ Tìm thấy lớp: {classroom.class_name} (ID={classroom.id})")
        hashed = hash_password(PASSWORD)
        created = 0

        for s in STUDENTS:
            # Create user if not exists
            user = db.query(User).filter(User.email == s["email"]).first()
            if not user:
                user = User(
                    email=s["email"],
                    password_hash=hashed,
                    full_name=s["full_name"],
                    role="student",
                    is_active=True,
                )
                db.add(user)
                db.flush()  # get user.id

            # Add to classroom if not already a member
            exists = (
                db.query(ClassroomStudent)
                .filter_by(classroom_id=classroom.id, student_id=user.id)
                .first()
            )
            if not exists:
                db.add(ClassroomStudent(classroom_id=classroom.id, student_id=user.id))
                created += 1
                print(f"  + {s['full_name']} ({s['email']})")

        db.commit()
        print(f"\n✔ Đã thêm {created} học sinh vào lớp {classroom.class_name}!")
        print(f"\n{'='*50}")
        print(f"📋 TÀI KHOẢN TEST:")
        print(f"   Email:    {STUDENTS[0]['email']}")
        print(f"   Password: {PASSWORD}")
        print(f"{'='*50}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
