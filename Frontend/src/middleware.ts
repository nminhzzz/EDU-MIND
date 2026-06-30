import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Hàm giải mã JWT siêu đơn giản (chỉ lấy phần dữ liệu giữa của Token)
function decodeJwt(token: string) {
  try {
    const base64Url = token.split(".")[1]; // JWT có dạng "Header.Payload.Signature", ta lấy Payload (phần thứ 2)
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/"); // Chuẩn hóa ký tự Base64Url về Base64
    const jsonStr = atob(base64); // Dịch ngược chuỗi Base64 ra chữ
    const payload = JSON.parse(jsonStr);
    
    // Kiểm tra thời gian hết hạn (exp) tính bằng giây
    if (payload.exp && payload.exp < Date.now() / 1000) {
      return null; // Token hết hạn thời gian -> Coi như không có token
    }
    return payload;
  } catch {
    return null;
  }
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Bước 1: Lấy Token từ trình duyệt và đọc thông tin người dùng
  const token = request.cookies.get("access_token")?.value;
  const user = token ? decodeJwt(token) : null;
  
  const isAuthenticated = !!user; // true nếu có token hợp lệ, ngược lại false
  const userRole = user?.role;    // "student" | "teacher" | "admin"

  // Bước 2: Phân loại các trang trong dự án
  const isAuthPage = pathname === "/login" || pathname === "/register";
  const isStudentPage = pathname.startsWith("/student");
  const isTeacherPage = pathname.startsWith("/teacher");
  const isAdminPage = pathname.startsWith("/admin");
  const isProtectedPage = isStudentPage || isTeacherPage || isAdminPage;

  // Bước 3: Nếu chưa đăng nhập mà cố tình vào các trang bảo vệ (student, teacher, admin)
  if (!isAuthenticated && isProtectedPage) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname); // Lưu lại trang định vào để đăng nhập xong quay lại ngay
    
    const response = NextResponse.redirect(loginUrl);
    // Xóa sạch cookie bị hỏng/hết hạn để tránh vòng lặp redirect
    response.cookies.delete("access_token");
    response.cookies.delete("refresh_token");
    return response;
  }

  // Bước 4: Nếu ĐÃ đăng nhập mà cố tình truy cập lại trang /login hoặc /register
  if (isAuthenticated && isAuthPage) {
    // Tự động đẩy thẳng vào Dashboard tương ứng: /student, /teacher hoặc /admin
    return NextResponse.redirect(new URL(`/${userRole}`, request.url));
  }

  // Bước 5: Nếu người dùng chưa đăng nhập và ở trang login/register -> Dọn dẹp các cookie rác (nếu còn sót lại)
  if (!isAuthenticated && isAuthPage) {
    const response = NextResponse.next();
    if (request.cookies.has("access_token")) {
      response.cookies.delete("access_token");
    }
    if (request.cookies.has("refresh_token")) {
      response.cookies.delete("refresh_token");
    }
    return response;
  }

  // Bước 6: Kiểm tra quyền truy cập của từng vai trò (Phân quyền - Authorization)
  if (isAuthenticated) {
    // Nếu vào trang học sinh nhưng KHÔNG PHẢI học sinh (và không phải admin)
    if (isStudentPage && userRole !== "student" && userRole !== "admin") {
      return NextResponse.redirect(new URL(`/${userRole}`, request.url)); // Đẩy về đúng trang của họ
    }
    
    // Nếu vào trang giáo viên nhưng KHÔNG PHẢI giáo viên (và không phải admin)
    if (isTeacherPage && userRole !== "teacher" && userRole !== "admin") {
      return NextResponse.redirect(new URL(`/${userRole}`, request.url));
    }

    // Nếu vào trang admin nhưng KHÔNG PHẢI admin
    if (isAdminPage && userRole !== "admin") {
      return NextResponse.redirect(new URL(`/${userRole}`, request.url));
    }
  }

  // Nếu mọi thứ hợp lệ, cho phép tiếp tục truy cập trang
  return NextResponse.next();
}


// Cấu hình các đường dẫn áp dụng middleware này (loại trừ file tĩnh như CSS, JS, ảnh)
export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:png|svg|jpg|jpeg|gif|webp)$).*)"],
};

