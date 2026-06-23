# Script sinh chứng chỉ SSL tự ký sử dụng Docker cho Windows (PowerShell)

# Tạo thư mục certs nếu chưa tồn tại
$certsDir = Join-Path $PSScriptRoot "certs"
if (!(Test-Path $certsDir)) {
    New-Item -ItemType Directory -Path $certsDir | Out-Null
}

Write-Host "=== Đang sinh chứng chỉ SSL tự ký qua Docker ===" -ForegroundColor Cyan

# Chạy container docker chứa openssl để xuất cert ra thư mục
docker run --rm -v "${certsDir}:/export" alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
  -keyout /export/localhost.key `
  -out /export/localhost.crt `
  -subj "/C=VN/ST=Hanoi/L=Hanoi/O=AI Learning Assistant Platform/CN=localhost"

Write-Host "=== Thành công! Chứng chỉ đã được lưu tại nginx/certs/ ===" -ForegroundColor Green
Get-ChildItem $certsDir
