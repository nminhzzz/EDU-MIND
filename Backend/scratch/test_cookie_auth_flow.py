import sys
import os

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

from fastapi.testclient import TestClient
from app.main import app
from app.database.mysql import SessionLocal
from app.models.user import User
from app.core.security import hash_password

def run_cookie_auth_test():
    print("--- KHỞI CHẠY KIỂM THỬ XÁC THỰC QUA COOKIES (TEST CLIENT) ---")
    
    # 1. Đảm bảo có user test trong DB
    db = SessionLocal()
    email = "cookie_student@test.com"
    password = "password123"
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name="Học Sinh Test Cookie",
            role="student",
            grade="Đại học năm 1",
            is_active=True
        )
        db.add(user)
        db.commit()
        print(f"Đã chuẩn bị tài khoản test: {email}")
    else:
        print(f"Tài khoản test đã sẵn sàng: {email}")
    db.close()

    client = TestClient(app)

    # 2. Test Login và nhận Cookie
    print("\n[Bước 1] Tiến hành đăng nhập bằng API /api/v1/auth/login...")
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    
    assert login_res.status_code == 200, f"Đăng nhập thất bại: {login_res.text}"
    print("  -> Đăng nhập thành công!")
    print(f"  -> Phản hồi: {login_res.json()}")

    # Kiểm tra cookies nhận được
    cookies = client.cookies
    print("\n[Kiểm tra cookies nhận được trong client]:")
    
    access_token_cookie = cookies.get("access_token")
    refresh_token_cookie = cookies.get("refresh_token")
    
    print(f"  - access_token cookie: {'Hoạt động' if access_token_cookie else 'Không tìm thấy'}")
    print(f"  - refresh_token cookie (HttpOnly): {'Hoạt động' if refresh_token_cookie else 'Không tìm thấy'}")
    
    assert access_token_cookie is not None, "Thiếu cookie access_token"
    assert refresh_token_cookie is not None, "Thiếu cookie refresh_token"

    # 3. Gọi /me sử dụng Cookie tự động của TestClient (Không truyền Header Authorization)
    print("\n[Bước 2] Gọi /me (không truyền Authorization Header, chỉ sử dụng cookies tự động)...")
    me_res = client.get("/api/v1/auth/me")
    
    assert me_res.status_code == 200, f"Không thể lấy thông tin /me bằng cookie: {me_res.text}"
    print("  -> Lấy thông tin cá nhân qua Cookie thành công!")
    print(f"  -> Người dùng: {me_res.json()['full_name']} | Email: {me_res.json()['email']}")

    # 4. Test API /refresh
    print("\n[Bước 3] Tiến hành gia hạn Token qua API /api/v1/auth/refresh...")
    refresh_res = client.post("/api/v1/auth/refresh")
    
    assert refresh_res.status_code == 200, f"Gia hạn token thất bại: {refresh_res.text}"
    print("  -> Gia hạn token thành công!")
    print(f"  -> Token mới: {refresh_res.json()['access_token'][:30]}...")

    # 5. Test Đăng xuất /logout
    print("\n[Bước 4] Tiến hành đăng xuất qua API /api/v1/auth/logout...")
    logout_res = client.post("/api/v1/auth/logout")
    
    assert logout_res.status_code == 200, "Đăng xuất thất bại"
    print("  -> Đăng xuất thành công!")

    # 6. Thử gọi lại /me sau khi đăng xuất
    print("\n[Bước 5] Gọi lại /me sau khi đăng xuất...")
    me_after_logout = client.get("/api/v1/auth/me")
    print(f"  -> Trạng thái phản hồi: {me_after_logout.status_code} (Mong muốn: 401)")
    assert me_after_logout.status_code == 401, "Người dùng vẫn đăng nhập sau khi logout!"
    print("  -> Chặn truy cập sau đăng xuất thành công!")

    print("\n=======================================================")
    print("     🎉 KIỂM THỬ XÁC THỰC QUA COOKIE THÀNH CÔNG!       ")
    print("=======================================================")

if __name__ == "__main__":
    run_cookie_auth_test()
