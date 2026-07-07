import requests
import io

BASE_URL = "http://127.0.0.1:8000"


def test_generic_upload():
    print("--- 1. LOGGING IN AS STUDENT ---")
    login_res = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": "student_test@edumind.com", "password": "studentpassword"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- 2. UPLOADING IMAGE (AVATAR) TO CLOUDINARY ---")
    # Tạo ảnh nháp giả lập (PNG bytes)
    img_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
    img_obj = io.BytesIO(img_content)

    files = {"file": ("student_avatar.png", img_obj, "image/png")}
    data = {"folder": "avatars"}

    upload_res = requests.post(
        f"{BASE_URL}/api/v1/uploads/", data=data, files=files, headers=headers
    )

    print(f"Upload Status Code: {upload_res.status_code}")
    assert upload_res.status_code == 201

    res_data = upload_res.json()
    url = res_data["url"]
    print(f"Uploaded Image URL: {url}")
    print(f"Response details: {res_data}")

    # Kiểm tra xem đường dẫn có trỏ về Cloudinary không và folder là avatars
    assert "cloudinary" in url.lower()
    assert res_data["filename"] == "student_avatar.png"
    assert res_data["file_type"] == "png"
    assert res_data["folder"] == "avatars"

    print("\n🎉 ALL TESTS PASSED: GENERIC UPLOAD WORKS PERFECTLY FOR IMAGES!")


if __name__ == "__main__":
    test_generic_upload()
