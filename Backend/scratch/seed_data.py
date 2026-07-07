import sys
import os
import asyncio
from datetime import datetime

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
from app.database.mysql import engine, SessionLocal
from app.database.mongodb import get_mongodb_db
from app.models.base import Base

# Import all models
from app.models.user import User
from app.models.student_preference import StudentPreference
from app.models.subject import Subject
from app.models.classroom import Classroom
from app.models.classroom_student import ClassroomStudent
from app.services.embedding_service import save_study_material

# Dữ liệu tài liệu học tập để làm RAG
MATERIALS_DATA = {
    "TRIETHOC": [
        {
            "topic": "Vật chất và ý thức",
            "content": "Vật chất là một phạm trù triết học dùng để chỉ thực tại khách quan được đem lại cho con người trong cảm giác, được cảm giác của chúng ta chép lại, chụp lại, phản ánh, và tồn tại không lệ thuộc vào cảm giác. Ý thức là sự phản ánh năng động, sáng tạo thế giới khách quan vào bộ óc người, là hình ảnh chủ quan của thế giới khách quan. Ý thức chịu ảnh hưởng của vật chất quyết định nhưng cũng có tính độc lập tương đối.",
        },
        {
            "topic": "Phép biện chứng duy vật",
            "content": "Phép biện chứng duy vật là khoa học về những quy luật phổ biến của sự vận động và phát triển của tự nhiên, của xã hội loài người và của tư duy. Có hai nguyên lý chính: nguyên lý về mối liên hệ phổ biến và nguyên lý về sự phát triển. Có ba quy luật cốt lõi: Quy luật lượng - chất (quy luật chuyển hóa từ những sự thay đổi về lượng thành những thay đổi về chất và ngược lại), Quy luật thống nhất và đấu tranh của các mặt đối lập (mâu thuẫn), và Quy luật phủ định của phủ định.",
        },
    ],
    "JAVA": [
        {
            "topic": "Lập trình hướng đối tượng trong Java",
            "content": "Java là một ngôn ngữ lập trình hướng đối tượng (OOP). OOP có bốn tính chất cơ bản: 1. Tính đóng gói (Encapsulation) che giấu chi tiết cài đặt bằng access modifiers (private, public, protected). 2. Tính kế thừa (Inheritance) cho phép lớp con kế thừa thuộc tính/phương thức lớp cha qua từ khóa extends. 3. Tính đa hình (Polymorphism) cho phép overriding (ghi đè ở lớp con) và overloading (nạp chồng phương thức cùng tên khác tham số). 4. Tính trừu tượng (Abstraction) sử dụng abstract class và interface để mô hình hóa thực thể.",
        },
        {
            "topic": "Quản lý bộ nhớ và Garbage Collection",
            "content": "Bộ nhớ trong Java được chia thành Stack và Heap. Stack lưu trữ các biến cục bộ và các tham chiếu đối tượng. Heap lưu trữ các đối tượng thực tế được khởi tạo bằng từ khóa new. Java tự động quản lý bộ nhớ thông qua bộ dọn rác Garbage Collector (GC). GC tự động quét và giải phóng các đối tượng trên Heap không còn tham chiếu nào trỏ tới, giúp lập trình viên tránh được lỗi rò rỉ bộ nhớ (memory leak).",
        },
    ],
    "CSHARP": [
        {
            "topic": "C# LINQ (Language Integrated Query)",
            "content": "LINQ (Language Integrated Query) là tính năng cực kỳ mạnh mẽ trong C# cho phép truy vấn dữ liệu từ nhiều nguồn khác nhau (Collections, XML, SQL Databases) trực tiếp bằng cú pháp giống SQL trong code. LINQ hỗ trợ hai loại cú pháp: Query Syntax (from x in list where x > 5 select x) và Method Syntax sử dụng Lambda Expressions (list.Where(x => x > 5)). Các phương thức LINQ thông dụng gồm Select, Where, OrderBy, GroupBy, Join, và Aggregate.",
        },
        {
            "topic": "C# Asynchronous Programming",
            "content": "C# hỗ trợ lập trình bất đồng bộ hiệu năng cao thông qua mô hình async và await. Một phương thức bất đồng bộ được đánh dấu bằng từ khóa async và trả về một Task hoặc Task<T>. Từ khóa await được đặt trước một tác vụ bất đồng bộ để tạm dừng thực thi phương thức hiện tại cho đến khi tác vụ đó hoàn thành, giúp giải phóng luồng chính (main thread) để UI không bị đơ hoặc máy chủ không bị nghẽn.",
        },
    ],
}


async def seed_data():
    print("--- BẮT ĐẦU SEED DỮ LIỆU MẪU HỆ THỐNG ---")

    # 1. Tạo bảng MySQL
    print("1. Đồng bộ cơ sở dữ liệu MySQL...")
    from sqlalchemy import text

    try:
        print("   * Đang dọn dẹp các bảng cũ (drop_all)...")
        with engine.connect() as conn:
            # Tắt kiểm tra khóa ngoại để tránh lỗi ràng buộc cũ
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            Base.metadata.drop_all(bind=conn)
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            conn.commit()

        print("   * Đang khởi tạo cấu trúc bảng mới (create_all)...")
        Base.metadata.create_all(bind=engine)
        print("   -> Đồng bộ thành công!")
    except Exception as ddl_err:
        print(f"   ❌ Lỗi khi đồng bộ cấu trúc bảng: {ddl_err}")
        raise ddl_err

    db: Session = SessionLocal()
    db_mongo = get_mongodb_db()

    try:
        # 2. Seed Users
        print("2. Đang seed tài khoản Giáo viên và Học sinh...")
        from app.core.security import hash_password

        # Tạo Giáo viên
        teacher = db.query(User).filter(User.email == "teacher@test.com").first()
        if not teacher:
            teacher = User(
                email="teacher@test.com",
                password_hash=hash_password("password123"),
                full_name="Thầy Nguyễn Hoàng Java",
                role="teacher",
                is_active=True,
            )
            db.add(teacher)
            db.commit()
            db.refresh(teacher)
            print(f"  -> Tạo Giáo viên thành công, ID: {teacher.id}")
        else:
            print(f"  -> Giáo viên đã tồn tại, ID: {teacher.id}")

        # Tạo Học sinh
        student = db.query(User).filter(User.email == "student@test.com").first()
        if not student:
            student = User(
                email="student@test.com",
                password_hash=hash_password("password123"),
                full_name="Trần Văn Học",
                role="student",
                is_active=True,
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            print(f"  -> Tạo Học sinh thành công, ID: {student.id}")
        else:
            print(f"  -> Học sinh đã tồn tại, ID: {student.id}")

        # Seed Student Preferences
        pref = (
            db.query(StudentPreference)
            .filter(StudentPreference.student_id == student.id)
            .first()
        )
        if not pref:
            pref = StudentPreference(
                student_id=student.id,
                study_hours_per_day=2,
                preferred_study_time="evening",
                available_schedule={
                    "mon": {"morning": True, "afternoon": False, "evening": True},
                    "tue": {"morning": True, "afternoon": True, "evening": True},
                    "wed": {"morning": False, "afternoon": True, "evening": True},
                    "thu": {"morning": True, "afternoon": False, "evening": True},
                    "fri": {"morning": True, "afternoon": True, "evening": False},
                    "sat": {"morning": False, "afternoon": False, "evening": False},
                    "sun": {"morning": False, "afternoon": False, "evening": False},
                },
            )
            db.add(pref)
            db.commit()
            print("  -> Đã seed cài đặt thời gian rảnh cho Học sinh.")

        # 3. Seed Subjects
        print("3. Đang seed môn học (Triết, Java, C#)...")
        subjects_map = {}
        subjects_data = [
            ("Triết học Mác - Lênin", "TRIETHOC", "Môn học Triết học đại cương"),
            ("Lập trình Java", "JAVA", "Lập trình hướng đối tượng với ngôn ngữ Java"),
            ("Lập trình C#", "CSHARP", "Lập trình ứng dụng với C# và .NET Framework"),
        ]

        for name, code, desc in subjects_data:
            subj = db.query(Subject).filter(Subject.code == code).first()
            if not subj:
                subj = Subject(name=name, code=code, description=desc)
                db.add(subj)
                db.commit()
                db.refresh(subj)
                print(f"  -> Đã tạo môn học: {name}")
            else:
                print(f"  -> Môn học đã tồn tại: {name}")
            subjects_map[code] = subj

        # 4. Seed Classrooms
        print("4. Đang seed Lớp học và gán học sinh/môn học...")
        classrooms_data = [
            (
                "CLASS_TRIETHOC",
                "Lớp Triết học Cơ bản",
                "Môn Triết học đại cương cho tân sinh viên",
                "TRIETHOC",
            ),
            (
                "CLASS_JAVA",
                "Lớp Lập trình Java OOP",
                "Hướng đối tượng Java cơ bản đến nâng cao",
                "JAVA",
            ),
            (
                "CLASS_CSHARP",
                "Lớp Lập trình C# chuyên sâu",
                "Lập trình C# / .NET / LINQ",
                "CSHARP",
            ),
        ]

        for code, name, desc, subj_code in classrooms_data:
            subj = subjects_map[subj_code]
            classroom = db.query(Classroom).filter(Classroom.class_code == code).first()
            if not classroom:
                classroom = Classroom(
                    teacher_id=teacher.id,
                    subject_id=subj.id,
                    class_name=name,
                    class_code=code,
                    description=desc,
                )
                db.add(classroom)
                db.commit()
                db.refresh(classroom)
                print(f"  -> Đã tạo lớp học: {name} (Mã: {code}) - Môn: {subj.name}")
            else:
                print(f"  -> Lớp học đã tồn tại: {name} (Mã: {code})")

            # Cho học sinh tham gia lớp (ClassroomStudent)
            class_student = (
                db.query(ClassroomStudent)
                .filter(
                    ClassroomStudent.classroom_id == classroom.id,
                    ClassroomStudent.student_id == student.id,
                )
                .first()
            )
            if not class_student:
                class_student = ClassroomStudent(
                    classroom_id=classroom.id, student_id=student.id
                )
                db.add(class_student)
                db.commit()
                print(f"     * Cho học sinh '{student.full_name}' tham gia lớp")

        # 5. Seed MongoDB Embeddings (RAG Data)
        print("5. Đang sinh Vector Embeddings và seed tài liệu học tập vào MongoDB...")
        # Dọn dẹp MongoDB collection để đồng bộ ID mới từ MySQL
        print("   * Đang dọn dẹp collection study_material_embeddings cũ...")
        await db_mongo.study_material_embeddings.delete_many({})

        for subj_code, chunks in MATERIALS_DATA.items():
            subj = subjects_map[subj_code]
            for chunk in chunks:
                print(
                    f"  -> Đang embed chủ đề '{chunk['topic']}' của môn {subj_code}..."
                )
                try:
                    inserted_id = await save_study_material(
                        db_mongo=db_mongo,
                        subject_id=subj.id,
                        topic=chunk["topic"],
                        content=chunk["content"],
                        metadata={
                            "source": "Giáo trình chính thống",
                            "author": "Hệ thống",
                        },
                    )
                    print(f"     * Thành công! Lưu MongoDB ObjectId: {inserted_id}")
                except Exception as embed_err:
                    print(f"     ❌ Thất bại: {embed_err}")

        print("\n=======================================================")
        print("    🎉 SEED DỮ LIỆU THÀNH CÔNG! HỆ THỐNG ĐÃ SẴN SÀNG    ")
        print("=======================================================")

    except Exception as err:
        print(f"\n❌ LỖI TRONG QUÁ TRÌNH SEED DỮ LIỆU: {err}")
    finally:
        db.close()


if __name__ == "__main__":
    # Đảm bảo có thể chạy async
    asyncio.run(seed_data())
