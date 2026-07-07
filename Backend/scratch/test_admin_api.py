import requests

BASE_URL = "http://localhost:8000/api/v1"


def test_admin_flow():
    print("--- 1. BẮT ĐẦU ĐĂNG NHẬP VỚI TÀI KHOẢN ADMIN ---")
    login_payload = {"email": "admin@edumind.com", "password": "adminpassword"}

    response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    if response.status_code != 200:
        print(f"Đăng nhập thất bại! Status code: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    token = data.get("access_token")
    print("Đăng nhập thành công! Token trích xuất:")
    print(f"  Token: {token[:30]}...{token[-30:]}")

    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- 2. KIỂM TRA API ADMIN ANALYTICS ---")
    analytics_res = requests.get(f"{BASE_URL}/analytics/admin/system", headers=headers)
    if analytics_res.status_code == 200:
        print("Gọi API Analytics thành công! Dữ liệu nhận được:")
        import json

        print(json.dumps(analytics_res.json(), indent=2, ensure_ascii=False))
    else:
        print(f"Lỗi khi gọi API Analytics: {analytics_res.status_code}")
        print(analytics_res.text)

    print("\n--- 3. KIỂM TRA API ADMIN GET USERS ---")
    users_res = requests.get(f"{BASE_URL}/users/admin/users", headers=headers)
    if users_res.status_code == 200:
        print(
            f"Gọi API Get Users thành công! Tìm thấy {len(users_res.json())} người dùng."
        )
        users_list = users_res.json()
        for idx, u in enumerate(users_list[:5]):
            print(
                f"  User {idx+1}: {u.get('email')} - Vai trò: {u.get('role')} - Active: {u.get('is_active')}"
            )
    else:
        print(f"Lỗi khi gọi API Get Users: {users_res.status_code}")
        print(users_res.text)


if __name__ == "__main__":
    test_admin_flow()
