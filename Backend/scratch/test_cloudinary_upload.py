import requests
import io

BASE_URL = "http://127.0.0.1:8000"


def test_cloudinary_upload():
    print("--- 1. LOGGING IN AS TEACHER ---")
    login_res = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": "teacher@edumind.com", "password": "teacherpassword"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- 2. UPLOADING FILE TO CLOUDINARY ---")
    # Tạo file nháp giả lập dạng bytes trong memory
    file_content = b"Day la tai lieu kiem thu de kiem tra tinh nang upload Cloudinary. Triet hoc Mac-Lenin la khoa hoc ve nhung quy luat chung nhat."
    file_obj = io.BytesIO(file_content)

    files = {"file": ("test_cloudinary_doc.txt", file_obj, "text/plain")}
    data = {"subject_id": 1, "title": "Tài liệu kiểm thử Cloudinary"}

    upload_res = requests.post(
        f"{BASE_URL}/api/v1/documents/", data=data, files=files, headers=headers
    )

    print(f"Upload Status Code: {upload_res.status_code}")
    assert upload_res.status_code == 201

    doc_data = upload_res.json()
    file_path = doc_data["file_path"]
    doc_id = doc_data["id"]
    print(f"Uploaded Document ID: {doc_id}")
    print(f"Uploaded Document File Path: {file_path}")

    # Kiểm tra xem đường dẫn có trỏ về Cloudinary không (thường chứa res.cloudinary.com)
    is_cloudinary = "cloudinary" in file_path.lower()
    print(f"Is Cloudinary URL? {is_cloudinary}")
    assert is_cloudinary, "File path should be a Cloudinary URL!"

    print("\n--- 3. CLEANING UP (DELETING DOCUMENT) ---")
    delete_res = requests.delete(
        f"{BASE_URL}/api/v1/documents/{doc_id}", headers=headers
    )
    print(f"Delete Status Code: {delete_res.status_code}")
    assert delete_res.status_code == 200
    print(f"Response: {delete_res.json()}")

    print("\n🎉 ALL TESTS PASSED: CLOUDINARY UPLOAD WORKS PERFECTLY!")


if __name__ == "__main__":
    test_cloudinary_upload()
