#!/bin/bash
# Script sinh chứng chỉ SSL tự ký sử dụng Docker (Không yêu cầu cài openssl ở máy host)

# Di chuyển vào thư mục chứa script
cd "$(dirname "$0")"

# Tạo thư mục certs nếu chưa tồn tại
mkdir -p certs

echo "=== Đang sinh chứng chỉ SSL tự ký qua Docker ==="
docker run --rm -v "$(pwd)/certs:/export" alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /export/localhost.key \
  -out /export/localhost.crt \
  -subj "/C=VN/ST=Hanoi/L=Hanoi/O=AI Learning Assistant Platform/CN=localhost"

echo "=== Thành công! Chứng chỉ đã được lưu tại nginx/certs/ ==="
ls -l certs/
