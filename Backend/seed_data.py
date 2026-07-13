# -*- coding: utf-8 -*-
from app.database.mysql import SessionLocal
from app.models.user import User
from app.models.subject import Subject
from app.core.security import hash_password

def main():
    print("Seeding database...")
    db = SessionLocal()
    try:
        users_to_seed = [
            {
                "email": "admin@edumind.vn",
                "password": "adminpassword",
                "full_name": "Quản trị viên Hệ thống",
                "role": "admin",
            },
            {
                "email": "teacher@edumind.vn",
                "password": "teacherpassword",
                "full_name": "Giáo viên Hướng dẫn",
                "role": "teacher",
            },
            {
                "email": "student@edumind.vn",
                "password": "studentpassword",
                "full_name": "Học sinh Minh Lê",
                "role": "student",
            }
        ]

        for u in users_to_seed:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                print(f"Creating user: {u['email']}")
                db_user = User(
                    email=u["email"],
                    password_hash=hash_password(u["password"]),
                    full_name=u["full_name"],
                    role=u["role"],
                    is_active=True
                )
                db.add(db_user)
        
        subjects_to_seed = [
            {"code": "TOAN", "name": "Toán học", "description": "Môn Toán học phổ thông và nâng cao"},
            {"code": "LY", "name": "Vật lý", "description": "Môn Vật lý đại cương"},
            {"code": "HOA", "name": "Hóa học", "description": "Môn Hóa học cơ bản và hữu cơ"},
            {"code": "ANH", "name": "Tiếng Anh", "description": "Tiếng Anh giao tiếp và học thuật"},
            {"code": "TIN", "name": "Tin học", "description": "Lập trình căn bản và tư duy thuật toán"},
            {"code": "VAN", "name": "Ngữ văn", "description": "Văn học Việt Nam và thế giới"},
            {"code": "SINH", "name": "Sinh học", "description": "Sinh học tế bào và di truyền học"}
        ]

        for s in subjects_to_seed:
            existing = db.query(Subject).filter(Subject.code == s["code"]).first()
            if not existing:
                print(f"Creating subject: {s['name']} ({s['code']})")
                db_subject = Subject(
                    code=s["code"],
                    name=s["name"],
                    description=s["description"]
                )
                db.add(db_subject)
        
        db.commit()
        print("✔ Database seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    main()
