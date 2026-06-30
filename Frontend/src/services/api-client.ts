import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://localhost/api/v1";

// Khởi tạo instance Axios
export const apiClient = axios.create({
  baseURL: BASE_URL,
  withCredentials: true, // Rất quan trọng: cho phép gửi cookies (access_token/refresh_token)
  headers: {
    "Content-Type": "application/json",
    // Gửi header này để vượt qua kiểm soát CSRF của Backend FastAPI
    "X-Requested-With": "XMLHttpRequest",
  },
});

// Cơ chế xếp hàng các request bị lỗi 401 khi đang đợi refresh token
let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Response Interceptor để tự động refresh token
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Nếu gặp lỗi 401 (Unauthorized) và request chưa được thử lại trước đó
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      originalRequest.url !== "/auth/refresh" &&
      originalRequest.url !== "/auth/login"
    ) {
      // Nếu đã có một request khác đang tiến hành refresh, tạm giữ request này lại
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(() => {
            return apiClient(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Thực hiện POST gọi refresh token ngầm
        await apiClient.post("/auth/refresh");
        
        isRefreshing = false;
        processQueue(null);
        
        // Gọi lại request ban đầu với token mới đã nạp vào cookie
        return apiClient(originalRequest);
      } catch (refreshError) {
        isRefreshing = false;
        processQueue(refreshError, null);
        
        // Nếu refresh cũng thất bại -> Cả hai token đều hết hạn -> Logout chuyển hướng
        if (typeof window !== "undefined") {
          const currentPath = window.location.pathname;
          if (currentPath !== "/login" && currentPath !== "/register") {
            window.location.href = "/login";
          }
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
