import { apiClient } from "./api-client";
import { ApiMessageResponse } from "@/types/api";
import { AuthMessageResponse, RegisterRequest, User, StudentProfileDetail, StudentGrade } from "@/types/user";

export interface UpdateProfileRequest {
  full_name?: string;
  avatar_url?: string;
  grade?: StudentGrade;
}

export const userApi = {
  /** Đăng nhập — tokens được gửi qua HttpOnly cookies, không có trong body. */
  login: (email: string, password: string) =>
    apiClient.post<AuthMessageResponse>("/auth/login", { email, password }),

  /** Đăng ký tài khoản mới (Học sinh / Giáo viên). */
  register: (data: RegisterRequest) =>
    apiClient.post<User>("/auth/register", data),

  /** Đăng xuất — thu hồi tokens và xóa cookies. */
  logout: () => apiClient.post<ApiMessageResponse>("/auth/logout"),

  /** Lấy thông tin tài khoản đang đăng nhập. */
  getMe: () => apiClient.get<User>("/auth/me"),

  /** Lấy chi tiết hồ sơ cá nhân & báo cáo học tập/phân tích học lực của học sinh. */
  getProfile: () => apiClient.get<StudentProfileDetail>("/users/profile"),

  /** Cập nhật thông tin cá nhân của người dùng đang đăng nhập. */
  updateProfile: (data: UpdateProfileRequest) =>
    apiClient.patch<User>("/users/profile", data),

  /** Upload tệp ảnh đại diện từ máy tính. */
  uploadAvatar: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post<{ avatar_url: string }>("/users/profile/avatar", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};


export default userApi;
