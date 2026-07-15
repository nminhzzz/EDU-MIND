import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { getApiBaseUrl } from "@/config/api";

/**
 * Shared Axios instance for all browser API calls.
 *
 * - Sends HttpOnly auth cookies via withCredentials
 * - Silently refreshes on 401 via POST /auth/refresh (cookie-based rotation)
 * - CSRF is handled by the backend through Origin/Referer validation
 */

const BASE_URL = getApiBaseUrl();

type RetryableRequest = InternalAxiosRequestConfig & { _retry?: boolean };

type QueueItem = {
  resolve: () => void;
  reject: (error: unknown) => void;
};

export const apiClient = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  timeout: 120_000,
  headers: {
    "Content-Type": "application/json",
  },
});

let isRefreshing = false;
let failedQueue: QueueItem[] = [];

const processQueue = (error: unknown | null) => {
  failedQueue.forEach((item) => {
    if (error) item.reject(error);
    else item.resolve();
  });
  failedQueue = [];
};

const AUTH_SKIP_PATHS = new Set(["/auth/refresh", "/auth/login"]);

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableRequest | undefined;
    const status = error.response?.status;
    const requestUrl = originalRequest?.url ?? "";

    if (
      status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !AUTH_SKIP_PATHS.has(requestUrl)
    ) {
      if (isRefreshing) {
        return new Promise<void>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(() => apiClient(originalRequest));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await apiClient.post("/auth/refresh");
        isRefreshing = false;
        processQueue(null);
        return apiClient(originalRequest);
      } catch (refreshError) {
        isRefreshing = false;
        processQueue(refreshError);

        if (typeof window !== "undefined") {
          const currentPath = window.location.pathname;
          if (currentPath !== "/login" && currentPath !== "/register") {
            const params = new URLSearchParams({ redirect: currentPath });
            window.location.href = `/login?${params.toString()}`;
          }
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);
