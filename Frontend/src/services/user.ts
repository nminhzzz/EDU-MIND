import { apiClient } from "./api-client";
import { User } from "@/types/user";

export const userApi = {
  /**
   * Đăng nhập tài khoản bằng email và mật khẩu
   */
  login: (email: string, password: string) => 
    apiClient.post<{ message: string; access_token: string; token_type: string }>("/auth/login", { email, password }),

  /**
   * Đăng ký tài khoản người dùng mới (Học sinh / Giáo viên)
   */
  register: (data: any) => 
    apiClient.post<User>("/auth/register", data),

  /**
   * Đăng xuất hệ thống, thu hồi tokens và xóa cookies
   */
  logout: () => 
    apiClient.post<{ message: string }>("/auth/logout"),

  /**
   * Lấy thông tin chi tiết tài khoản đang đăng nhập hiện tại
   */
  getMe: () => 
    apiClient.get<User>("/auth/me"),
};
export default userApi;
