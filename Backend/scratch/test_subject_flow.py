import sys
import os

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
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate
from app.services.subject_service import (
    create_subject,
    get_subject,
    get_all_subjects,
    update_subject,
    delete_subject
)


def run_subject_flow_test():
    print("=== BẮT ĐẦU CHẠY THỬ NGHIỆM TÍCH HỢP 4 TẦNG (APIS MÔN HỌC) ===")
    
    db: Session = SessionLocal()
    
    try:
        # Xóa môn học test cũ nếu có
        test_code = "PYTHON_TEST"
        db.query(Subject).filter(Subject.code == test_code).delete()
        db.commit()

        # 1. Tạo môn học mới
        print("\nStep 1: Tạo môn học mới qua Service...")
        subj_in = SubjectCreate(
            name="Lập trình Python cơ bản",
            code=test_code,
            description="Môn học lập trình cơ bản bằng Python"
        )
        subj = create_subject(db=db, obj_in=subj_in)
        print(f"  -> Tạo môn học thành công! ID: {subj.id}, Name: {subj.name}, Code: {subj.code}")
        assert subj.id is not None
        assert subj.code == test_code

        # 2. Kiểm tra tính duy nhất (trùng mã code)
        print("\nStep 2: Kiểm tra tính duy nhất của mã môn học...")
        try:
            create_subject(db=db, obj_in=subj_in)
            print("❌ Lỗi: Lẽ ra hệ thống phải chặn trùng mã code môn học!")
            return
        except ValueError as ve:
            print(f"  -> Thành công: Hệ thống chặn trùng code với thông báo: '{ve}'")

        # 3. Truy xuất chi tiết môn học
        print("\nStep 3: Xem chi tiết môn học vừa tạo...")
        fetched_subj = get_subject(db=db, subject_id=subj.id)
        print(f"  -> Lấy thành công! Name: {fetched_subj.name}, Desc: {fetched_subj.description}")
        assert fetched_subj.name == "Lập trình Python cơ bản"

        # 4. Lấy tất cả môn học
        print("\nStep 4: Lấy danh sách tất cả môn học...")
        all_subjs = get_all_subjects(db=db)
        print(f"  -> Tổng số môn học hiện có: {len(all_subjs)}")
        assert len(all_subjs) >= 1
        assert any(s.code == test_code for s in all_subjs)

        # 5. Cập nhật môn học
        print("\nStep 5: Cập nhật môn học...")
        update_in = SubjectUpdate(
            name="Lập trình Python nâng cao",
            description="Môn học lập trình nâng cao bằng Python 3.13"
        )
        updated = update_subject(db=db, subject_id=subj.id, obj_in=update_in)
        print(f"  -> Cập nhật thành công! Name: {updated.name}, Desc: {updated.description}")
        assert updated.name == "Lập trình Python nâng cao"

        # 6. Xóa môn học
        print("\nStep 6: Xóa môn học...")
        deleted = delete_subject(db=db, subject_id=subj.id)
        print(f"  -> Xóa thành công môn học ID: {deleted.id}")
        
        # Thử lấy lại để xác nhận đã xóa
        try:
            get_subject(db=db, subject_id=subj.id)
            print("❌ Lỗi: Môn học vẫn tồn tại sau khi xóa!")
            return
        except ValueError:
            print("  -> Xác nhận: Môn học đã hoàn toàn biến mất khỏi cơ sở dữ liệu.")

        print("\n=======================================================")
        print("      🎉 KIỂM THỬ TÍCH HỢP 4 TẦNG APIS MÔN HỌC THÀNH CÔNG!     ")
        print("=======================================================")

    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình chạy test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    run_subject_flow_test()
